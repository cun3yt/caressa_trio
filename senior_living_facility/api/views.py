import pytz

from django.db.models import Q, Count
from rest_framework import viewsets, mixins, status, views
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from alexa.api.permissions import IsSenior
from alexa.api.serializers import UserSerializer
from alexa.models import User
from caressa import settings
from senior_living_facility.api.permissions import IsFacilityOrgMember, IsUserInFacility, IsInSameFacility
from senior_living_facility.api import serializers as facility_serializers
from senior_living_facility.api import calendar_serializers as calendar_serializers
from senior_living_facility import models as facility_models
from django.utils import timezone
from datetime import datetime, timedelta

from senior_living_facility.models import SeniorLivingFacility
from utilities import file_operations as file_ops
from utilities.time import now_in_tz, today_in_tz, time_today_in_tz
from utilities.views.mixins import ForAdminApplicationMixin


class SeniorLivingFacilityViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, IsUserInFacility, )
    queryset = facility_models.SeniorLivingFacility.objects.all()
    serializer_class = facility_serializers.SeniorLivingFacilitySerializer


class ServiceRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = facility_models.ServiceRequest.objects.all()
    serializer_class = facility_serializers.ServiceRequestSerializer


class FacilityTimeState(views.APIView):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )

    def get(self, request, pk, format=None):
        assert self.facility == request.user.senior_living_facility, (
            "No access for this calendar"
        )

        is_status_changeable = self.facility.is_morning_status_changeable
        next_cut_off = self.facility.next_morning_status_cut_off_time

        tz = self.facility.timezone

        return Response({
            'timezone': tz,
            'current_time': now_in_tz(tz),
            'status': "morning-status-available" if is_status_changeable else "morning-status-not-available",
            'status_change_datetime': next_cut_off
        })

    @property
    def facility(self):
        pk = self.kwargs.get('pk')
        return SeniorLivingFacility.objects.get(pk=pk)


class FacilityViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet, ForAdminApplicationMixin):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, IsUserInFacility, )
    queryset = facility_models.SeniorLivingFacility.objects.all()
    serializer_class = facility_serializers.FacilitySerializer


class FacilityListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    serializer_classes = {
        'staff-checked': facility_serializers.MorningCheckInDoneByStaffSerializer,
        'notified': facility_serializers.MorningCheckInNotDoneSerializer,
        'self-checked': facility_serializers.MorningCheckInDoneByUserSerializer,
        'pending': facility_serializers.MorningCheckInNotDoneSerializer,
    }

    @property
    def is_morning_check_in_requested(self) -> bool:
        return self.request.query_params.get('view') == 'morning-check-in'

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if self.is_morning_check_in_requested:
            result_set = {}
            for _status, queryset_group in queryset.items():
                serializer = self.serializer_classes.get(_status)
                if serializer is None:
                    continue
                result_set[_status] = queryset_group
                result_set[_status]['residents'] = serializer(result_set[_status]['residents'], many=True).data
            return Response(result_set)

        serializer = facility_serializers.AdminAppSeniorListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        facility = self.request.user.senior_living_facility     # type: facility_models.SeniorLivingFacility

        if self.is_morning_check_in_requested:
            return facility.residents_grouped_by_state
        return facility.residents.order_by('first_name', 'room_no')


class FacilityMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, IsFacilityOrgMember,)  # todo add check for message readability for user
    queryset = facility_models.Message.objects.all()
    serializer_class = facility_serializers.FacilityMessageSerializer


class MessagesThreadParticipantViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )  # todo add check for message readability for user
    queryset = facility_models.SeniorLivingFacilityMockMessageData.objects.all()
    serializer_class = facility_serializers.MessageThreadParticipantSerializer

    @property
    def facility(self):
        facility_id = self.kwargs.get('pk')
        return facility_models.SeniorLivingFacility.objects.get(id=facility_id)

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination

    def get_queryset(self):
        return facility_models.MessageThreadParticipant.objects.filter(senior_living_facility=self.facility)


class FacilityResidentTodayCheckInViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, IsInSameFacility, )
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @property
    def senior(self):
        senior_id = self.kwargs.get('pk')
        return User.objects.get(id=senior_id)

    def create(self, request, *args, **kwargs):
        """
        Creating a check-in for today. If it exists it sets the `checked` time to now and the `staff` that checked.
        """

        staff = request.user    # type: User
        checked = datetime.now(pytz.utc)
        today = today_in_tz(staff.senior_living_facility.timezone)
        check_in, _ = facility_models.FacilityCheckInOperationForSenior.objects\
            .update_or_create(senior=self.senior, date=today, defaults={'checked': checked, 'staff': staff})
        # todo return the check in data
        return Response({'success': True}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Destroying today's check-in. Staff is filled with whom deleted the entry
        """

        staff = request.user
        today = today_in_tz(staff.senior_living_facility.timezone)
        check_in, _ = facility_models.FacilityCheckInOperationForSenior.objects\
            .update_or_create(senior=self.senior, date=today, defaults={'checked': None, 'staff': staff})
        return Response({'success': True}, status=status.HTTP_202_ACCEPTED)


class MessageThreadMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = facility_serializers.MessageSerializer

    @property
    def message_thread(self):
        message_thread_id = self.kwargs.get('pk')
        return facility_models.MessageThread.objects.get(id=message_thread_id)

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination

    def get_queryset(self):
        return facility_models.Message.objects.filter(message_thread=self.message_thread)


class MessageThreadViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    queryset = facility_models.MessageThread
    serializer_class = facility_serializers.MessageThreadSerializer


class SeniorDeviceUserActivityLogCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = facility_models.SeniorDeviceUserActivityLog
    serializer_class = facility_serializers.SeniorDeviceUserActivityLogSerializer


class SeniorLivingFacilityContentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    serializer_class = facility_serializers.SeniorLivingFacilityContentSerializer

    def get_queryset(self):
        """
        Currently limited to the injectable contents

        :return:
        """
        user = self.request.user
        facility = user.senior_living_facility

        now = datetime.now(timezone.utc)
        return facility_models.SeniorLivingFacilityContent.objects.\
            filter(senior_living_facility=facility, delivery_rule__end__gte=now,
                   delivery_rule__type=facility_models.ContentDeliveryRule.TYPE_INJECTABLE)\
            .filter(Q(delivery_rule__recipient_ids__isnull=True) | Q(delivery_rule__recipient_ids__contains=[user.id]))


class PhotoGalleryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = facility_serializers.PhotoGallerySerializer

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination

    def get_queryset(self):
        dist = facility_models.Photo.objects.values('date').annotate(date_count=Count('date')).filter(date_count=1)
        single_dates = facility_models.Photo.objects.filter(date__in=[item['date'] for item in dist])
        return single_dates


class PhotosDayViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = facility_serializers.PhotosDaySerializer

    @property
    def date(self):
        return self.kwargs.get('date')

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 10

    pagination_class = _Pagination

    def get_queryset(self):
        datetime_obj = datetime.strptime(self.date, '%Y-%m-%d')
        return facility_models.Photo.objects.filter(date=datetime_obj)


class CalendarViewSet(views.APIView):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )

    def get(self, request, pk, format=None):
        """
        Returns the calendar events for the days of the given day GET parameter `start` +/- day_delta.
        """

        plus_minus_day_delta = 7
        date_format = "%A, %B %d, %Y"   # e.g. Monday, April 08, 2019
        start = request.query_params.get('start')
        start_datetime = datetime.strptime(start, '%Y-%m-%d') - timedelta(days=plus_minus_day_delta)

        assert self.facility == request.user.senior_living_facility, (
            "No access for this calendar"
        )

        interval = [
            {
                'date': (start_datetime + timedelta(days=day_increment)).strftime(date_format),
                'events': self.facility.get_given_day_events(start_datetime + timedelta(days=day_increment))
            } for day_increment in range(0, (2 * plus_minus_day_delta + 1))
        ]
        data = calendar_serializers.CalendarDateSerializer(interval, many=True).data
        return Response(data)

    @property
    def facility(self):
        pk = self.kwargs.get('pk')
        return SeniorLivingFacility.objects.get(pk=pk)


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def new_profile_picture(request, **kwargs):
    instance_type = kwargs.get('instance', None)
    instance_model = SeniorLivingFacility if instance_type == 'facility' else User
    instance_id = kwargs.get('id', None)

    instance = instance_model.objects.filter(pk=instance_id)[0]
    file_name = request.data.get('key')

    current_instance_profile_pic = instance.profile_pic

    new_profile_pic_hash_version = file_ops.generate_versioned_picture_name(current_instance_profile_pic)

    file_ops.download_to_tmp_from_s3(file_name, settings.S3_RAW_UPLOAD_BUCKET)

    save_picture_format = 'jpg'
    picture_set = file_ops.profile_picture_resizing_wrapper(file_name, new_profile_pic_hash_version,
                                                            save_picture_format)
    file_ops.upload_to_s3_from_tmp(settings.S3_PRODUCTION_BUCKET, picture_set, instance.id, instance_type)

    instance.profile_pic = new_profile_pic_hash_version.rsplit('.')[0]
    instance.save()
    pics = instance.get_profile_pictures()

    return Response({
        'message': 'Profile Picture Updated',
        'profile_picture_url': pics.get('w_250'),
        'thumbnail_url': pics.get('w_25'),
    })