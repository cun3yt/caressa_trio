from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from alexa.api.permissions import IsSenior, IsFacilityOrgMemberAndCanSeeSenior
from alexa.api.views import SeniorListViewSet
from alexa.models import User
from senior_living_facility.api.permissions import IsFacilityOrgMember
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog
from senior_living_facility.api.serializers import SeniorLivingFacilitySerializer, \
    SeniorDeviceUserActivityLogSerializer, FacilitySerializer, AdminAppSeniorListSerializer, \
    MorningCheckingUserPendingSerializer, MorningCheckingUserNotifiedSerializer, \
    MorningCheckingUserStaffCheckedSerializer, MorningCheckingUserSelfCheckedSerializer


class SeniorLivingFacilityViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = SeniorLivingFacilitySerializer


class FacilityViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = FacilitySerializer


class FacilityListViewSet(SeniorListViewSet):
    pagination_class = None

    def get_serializer_class(self, *args, **kwargs):
        param = self.request.query_params.get('status', None)

        if param is None:
            return AdminAppSeniorListSerializer(*args, **kwargs)
        elif param == 'notified':
            return MorningCheckingUserNotifiedSerializer
        elif param == 'pending':
            return MorningCheckingUserPendingSerializer
        elif param == 'staff-checked':
            return MorningCheckingUserStaffCheckedSerializer
        elif param == 'self-checked':
            return MorningCheckingUserSelfCheckedSerializer

    def get_queryset(self):
        user = self.request.user
        slf_id = self.kwargs.get('senior_living_facility_id')
        param = self.request.query_params.get('status', None)
        if not user.is_provider():
            return []

        queryset = User.objects.filter(user_type__exact=User.CARETAKER,
                                       senior_living_facility=slf_id,
                                       is_active=True)

        if param is None:
            return queryset
        elif param == 'notified':
            return queryset
        elif param == 'pending':
            return queryset
        elif param == 'staff-checked':
            return queryset
        elif param == 'self-checked':
            return queryset


class SeniorDeviceUserActivityLogCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = SeniorDeviceUserActivityLog
    serializer_class = SeniorDeviceUserActivityLogSerializer
