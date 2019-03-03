from rest_framework.permissions import BasePermission
from alexa.models import User, Circle, UserSettings
from actions.models import Comment


class IsSameUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, User), (
            "The object that is tried to be reached supposed to be User, found: '%s'" % type(obj)
        )
        return obj.id == request.user.id


class IsInCircle(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Circle), (
            "The object that is tried to be reached supposed to be Circle, found: '%s'" % type(obj)
        )
        return obj.is_member(request.user)


class CanAccessUserSettings(BasePermission):
    def has_object_permission(self, request, view, obj):
        """ If settings belong to the request user, it is allowed.
        If settings belong to the senior, the request user must be the admin of that senior's circle
        """

        assert isinstance(obj, UserSettings), (
                "The object that is tried to be reached supposed to be UserSettings, found: '%s'" % type(obj)
        )
        user_settings = obj
        if user_settings.user == request.user:
            return True

        senior_user = user_settings.user

        if not senior_user.is_senior():
            return False

        return senior_user.senior_circle.is_admin(request.user)


class CommentAccessible(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Comment), (
            "The object that is tried to be reached supposed to be Comment, found: '%s'" % type(obj)
        )
        comment = obj # type: Comment
        user = comment.content.actor    # type: User
        circle = user.circle_set.all()[0]   # type: Circle
        return circle.is_member(request.user)


class IsFacilityMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_provider()

    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, User), (
                "The object that is tried to be reached supposed to be User, found: '%s'" % type(obj)
        )
        senior = obj
        if not senior.senior_living_facility:
            return False
        return senior.senior_living_facility == request.user.senior_living_facility
