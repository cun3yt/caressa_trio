from rest_framework.permissions import BasePermission

from alexa.models import User
from senior_living_facility.models import SeniorLivingFacility, Photo


class IsFacilityOrgMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_provider()


class IsUserInFacility(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, SeniorLivingFacility), (
                "The object that is tried to be reached supposed to be SeniorLivingFacility, found: '%s'" % type(obj)
        )
        senior_living_facility = obj
        return request.user.senior_living_facility == senior_living_facility


class IsInSameFacility(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, User), (
                "The object that is tried to be reached supposed to be User, found: '%s'" % type(obj)
        )
        senior = obj
        if not senior.senior_living_facility:
            return False
        return senior.senior_living_facility == request.user.senior_living_facility


class IsUserFacilitySameWithPhotoGalleryFacility(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Photo), (
                "The object that is tried to be reached supposed to be Photo, found: '%s'" % type(obj)
        )
        photo = obj
        if not photo.senior_living_facility:
            return False
        return photo.senior_living_facility == request.user.senior_living_facility