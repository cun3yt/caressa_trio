from rest_framework.permissions import BasePermission
from alexa.models import User, Circle
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


class CommentAccessible(BasePermission):
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Comment), (
            "The object that is tried to be reached supposed to be Comment, found: '%s'" % type(obj)
        )
        comment = obj # type: Comment
        user = comment.content.actor    # type: User
        circle = user.circle_set.all()[0]   # type: Circle
        return circle.is_member(request.user)
