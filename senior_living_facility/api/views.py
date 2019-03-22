from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from alexa.api.permissions import IsSenior, IsFacilityOrgMemberAndCanSeeSenior
from alexa.api.views import SeniorListViewSet
from alexa.models import User
from senior_living_facility.api.permissions import IsFacilityOrgMember
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog
from senior_living_facility.api.serializers import SeniorLivingFacilitySerializer, \
    SeniorDeviceUserActivityLogSerializer, FacilitySerializer, AdminAppSeniorListSerializer


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
    serializer_class = AdminAppSeniorListSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        slf_id = self.kwargs.get('senior_living_facility_id')
        if not user.is_provider():
            return []
        queryset = User.objects.filter(user_type__exact=User.CARETAKER,
                                       senior_living_facility=slf_id,
                                       is_active=True).all()
        return queryset


class FacilityMorningCheckinViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMemberAndCanSeeSenior, )
    # serializer_class = AdminAppMorningCheckInSerializer


class SeniorDeviceUserActivityLogCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSenior, )
    queryset = SeniorDeviceUserActivityLog
    serializer_class = SeniorDeviceUserActivityLogSerializer
