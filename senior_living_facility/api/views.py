from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from alexa.api.permissions import IsSenior
from alexa.api.views import SeniorListViewSet
from alexa.models import User
from caressa import settings
from senior_living_facility.api.permissions import IsFacilityOrgMember
from senior_living_facility.api.serializers import FacilitySerializer, AdminAppSeniorListSerializer, \
    MorningCheckinUserPendingSerializer, MorningCheckinUserNotifiedSerializer, \
    MorningCheckinUserStaffCheckedSerializer, MorningCheckinUserSelfCheckedSerializer, FacilityMessagesSerializer, \
    MessageThreadMessagesSerializer
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog, \
    SeniorLivingFacilityContent, ContentDeliveryRule, SeniorLivingFacilityMockMessageData, ServiceRequest
from senior_living_facility.models import SeniorLivingFacilityMockUserData as MockUserData
from senior_living_facility.api.serializers import SeniorLivingFacilitySerializer, \
    SeniorDeviceUserActivityLogSerializer, SeniorLivingFacilityContentSerializer, ServiceRequestSerializer
from django.utils import timezone
from datetime import datetime

from utilities.file_operations import generate_versioned_picture_name, download_to_tmp_from_s3, \
    profile_picture_resizing_wrapper, upload_to_s3_from_tmp
from utilities.views.mixins import ForAdminMixin


class SeniorLivingFacilityViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = SeniorLivingFacilitySerializer


class ServiceRequestViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer


class FacilityViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet, ForAdminMixin):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = FacilitySerializer


class FacilityListViewSet(SeniorListViewSet, ForAdminMixin):
    pagination_class = None

    def get_serializer_class(self, *args, **kwargs):
        param = self.request.query_params.get('status', None) or self.request.query_params.get('starts_with', None)

        if param is None:
            return AdminAppSeniorListSerializer
        elif param == 'notified':
            return MorningCheckinUserNotifiedSerializer
        elif param == 'pending':
            return MorningCheckinUserPendingSerializer
        elif param == 'staff-checked':
            return MorningCheckinUserStaffCheckedSerializer
        elif param == 'self-checked':
            return MorningCheckinUserSelfCheckedSerializer
        else:
            return AdminAppSeniorListSerializer

    def get_queryset(self):
        user = self.request.user
        param = self.request.query_params.get('status', None) or self.request.query_params.get('starts_with', None)
        if not user.is_provider():
            return []

        qs = MockUserData.objects.all()
        queryset = User.objects.filter(id__in=qs)

        if param is None:
            return queryset
        elif param == 'notified':
            qs = MockUserData.objects.all().filter(
                checkin_status=MockUserData.NOTIFIED)
            queryset = User.objects.all().filter(id__in=qs)
            return queryset
        elif param == 'pending':
            qs = MockUserData.objects.all().filter(
                checkin_status=MockUserData.PENDING)
            queryset = User.objects.all().filter(id__in=qs)
            return queryset
        elif param == 'staff-checked':
            qs = MockUserData.objects.all().filter(
                checkin_status=MockUserData.STAFF_CHECKED)
            queryset = User.objects.all().filter(id__in=qs)
            return queryset
        elif param == 'self-checked':
            qs = MockUserData.objects.all().filter(
                checkin_status=MockUserData.SELF_CHECKED)
            queryset = User.objects.all().filter(id__in=qs)
            return queryset
        else:  # param = starts_with parameter
            qs = MockUserData.objects.filter(senior__first_name__istartswith=param)
            queryset = User.objects.all().filter(id__in=qs)
            return queryset


class FacilityMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet, ForAdminMixin):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, IsFacilityOrgMember,)
    queryset = SeniorLivingFacilityMockMessageData.objects.all()
    serializer_class = FacilityMessagesSerializer

    class _Pagination(PageNumberPagination):
        max_page_size = 20
        page_size_query_param = 'page_size'
        page_size = 5

    pagination_class = _Pagination


class MessageThreadMessagesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet, ForAdminMixin):
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
