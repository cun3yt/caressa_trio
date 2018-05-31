from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from actions.api.serializers import ActionSerializer, CommentSerializer, ReactionSerializer
from actions.models import UserAction, Comment, UserReaction


class ActionViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ActionSerializer
    queryset = UserAction.objects.all().order_by('-timestamp')


class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-created', '-id')


class ReactionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ReactionSerializer
    queryset = UserReaction.objects.all().order_by('-id')
