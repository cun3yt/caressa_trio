from rest_framework.permissions import BasePermission
from alexa.models import User


class IsSameUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, User), (
                "The object that is tried to be reached supposed to be User, found: '%s'" % type(obj)
        )
        return obj.id == request.user.id
