from rest_framework.permissions import BasePermission
from streaming.models import UserContentRepository


class UserWithInjectedContentRepository(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_senior()

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, UserContentRepository), (
            "The object that is tried to be reached supposed to be InjectedContentRepository, found: '%s'" % type(obj)
        )
        return obj.user_id == request.user.id
