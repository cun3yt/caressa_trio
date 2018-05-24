from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from actions.api.serializers import ActionSerializer, CommentSerializer
from actions.models import UserAction, Comment


class ActionViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ActionSerializer
    queryset = UserAction.objects.all().order_by('-timestamp')


class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-created', '-id')
