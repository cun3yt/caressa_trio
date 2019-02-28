from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from senior_living_facility.api.permissions import IsFacilityOrgMember
from senior_living_facility.models import SeniorLivingFacility
from senior_living_facility.api.serializers import SeniorLivingFacilitySerializer


class SeniorLivingFacilityViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMember, )
    queryset = SeniorLivingFacility.objects.all()
    serializer_class = SeniorLivingFacilitySerializer
