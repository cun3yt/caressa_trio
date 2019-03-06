from rest_framework.permissions import BasePermission
from senior_living_facility.models import SeniorLivingFacility


class IsFacilityOrgMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_provider()

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, SeniorLivingFacility), (
                "The object that is tried to be reached supposed to be SeniorLivingFacility, found: '%s'" % type(obj)
        )
        senior_living_facility = obj
        return request.user.senior_living_facility == senior_living_facility
