import pytz

from django.db.models import Q, Count
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from alexa.api.permissions import IsSenior
from alexa.api.serializers import UserSerializer
from alexa.api.views import SeniorListViewSet
from alexa.models import User
from caressa import settings
from senior_living_facility.api.permissions import IsFacilityOrgMember, IsUserInFacility, IsInSameFacility
from senior_living_facility.api.serializers import FacilitySerializer, AdminAppSeniorListSerializer, \
    MorningCheckInUserNotifiedSerializer, \
    MorningCheckInUserStaffCheckedSerializer, MorningCheckInUserSelfCheckedSerializer, FacilityMessagesSerializer, \
    MessageThreadMessagesSerializer, FacilityMessageSerializer, PhotoGallerySerializer, PhotosDaySerializer
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog, \
    SeniorLivingFacilityContent, ContentDeliveryRule, SeniorLivingFacilityMockMessageData, ServiceRequest, Message, \
    FacilityCheckInOperationForSenior, FacilityPhoto
from senior_living_facility.api.serializers import SeniorLivingFacilitySerializer, \
    SeniorDeviceUserActivityLogSerializer, SeniorLivingFacilityContentSerializer, ServiceRequestSerializer
from django.utils import timezone
from datetime import datetime

from utilities.file_operations import generate_versioned_picture_name, download_to_tmp_from_s3, \
    profile_picture_resizing_wrapper, upload_to_s3_from_tmp
from utilities.time import today_in_tz
from utilities.views.mixins import ForAdminApplicationMixin


class SeniorLivingFacilityViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, IsUserInFacility, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = SeniorLivingFacilitySerializer


class ServiceRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer


class FacilityViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet, ForAdminApplicationMixin):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, IsUserInFacility, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = FacilitySerializer


class FacilityListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    serializer_classes = {
        'staff-checked': MorningCheckInUserStaffCheckedSerializer,
        'self-checked': MorningCheckInUserSelfCheckedSerializer,
        'pending': MorningCheckInUserNotifiedSerializer,
        'notified': MorningCheckInUserNotifiedSerializer,
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

        serializer = AdminAppSeniorListSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        facility = self.request.user.senior_living_facility     # type: SeniorLivingFacility

        if self.is_morning_check_in_requested:
            return FacilityCheckInOperationForSenior.get_seniors_grouped_by_state(facility=facility)
        return facility.residents


class FacilityMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, IsFacilityOrgMember,)  # todo add check for message readability for user
    queryset = Message.objects.all()
    serializer_class = FacilityMessageSerializer


class FacilityMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet, ForAdminApplicationMixin):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )  # todo add check for message readability for user
    queryset = SeniorLivingFacilityMockMessageData.objects.all()
    serializer_class = FacilityMessagesSerializer

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination


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
        check_in, _ = FacilityCheckInOperationForSenior.objects.update_or_create(senior=self.senior,
                                                                                 date=today,
                                                                                 defaults={
                                                                                     'checked': checked,
                                                                                     'staff': staff,
                                                                                 })
        # todo return the check in data
        return Response({'success': True}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Destroying today's check-in. Staff is filled with whom deleted the entry
        """

        staff = request.user
        today = today_in_tz(staff.senior_living_facility.timezone)
        check_in, _ = FacilityCheckInOperationForSenior.objects.update_or_create(senior=self.senior,
                                                                                 date=today,
                                                                                 defaults={
                                                                                     'checked': None,
                                                                                     'staff': staff,
                                                                                 })
        return Response({'success': True}, status=status.HTTP_204_NO_CONTENT)


class MessageThreadMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet, ForAdminApplicationMixin):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageThreadMessagesSerializer

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination

    def get_queryset(self):
        return SeniorLivingFacilityMockMessageData.objects.filter(senior=94).order_by('-id')


class SeniorDeviceUserActivityLogCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = SeniorDeviceUserActivityLog
    serializer_class = SeniorDeviceUserActivityLogSerializer


class SeniorLivingFacilityContentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    serializer_class = SeniorLivingFacilityContentSerializer

    def get_queryset(self):
        """
        Currently limited to the injectable contents

        :return:
        """
        user = self.request.user
        facility = user.senior_living_facility

        now = datetime.now(timezone.utc)
        return SeniorLivingFacilityContent.objects.filter(senior_living_facility=facility,
                                                          delivery_rule__end__gte=now,
                                                          delivery_rule__type=ContentDeliveryRule.TYPE_INJECTABLE)\
            .filter(Q(delivery_rule__recipient_ids__isnull=True) | Q(delivery_rule__recipient_ids__contains=[user.id]))


class PhotoGalleryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = PhotoGallerySerializer

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination

    def get_queryset(self):
        dist = FacilityPhoto.objects.values('date').annotate(date_count=Count('date')).filter(date_count=1)
        single_dates = FacilityPhoto.objects.filter(date__in=[item['date'] for item in dist])
        return single_dates


class PhotosDayViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = PhotosDaySerializer

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
        return FacilityPhoto.objects.filter(date=datetime_obj)


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def uploaded_new_profile_picture(request, **kwargs):
    user_id = kwargs.get('id', None)

    user = User.objects.filter(pk=user_id)[0]
    file_name = request.data.get('key')

    current_user_profile_pic = user.profile_pic

    new_profile_pic_hash_version = generate_versioned_picture_name(current_user_profile_pic)

    download_to_tmp_from_s3(file_name, settings.S3_RAW_UPLOAD_BUCKET)

    save_picture_format = 'jpg'
    picture_set = profile_picture_resizing_wrapper(file_name, new_profile_pic_hash_version, save_picture_format)
    upload_to_s3_from_tmp(settings.S3_PRODUCTION_BUCKET, picture_set, user.id)

    user.profile_pic = new_profile_pic_hash_version.rsplit('.')[0]
    user.save()
    pics = user.get_profile_pictures()

    return Response({
        'message': 'Profile Picture Updated',
        'profile_picture_url': pics.get('w_250'),
        'thumbnail_url': pics.get('w_25'),
    })
