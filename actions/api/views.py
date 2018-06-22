from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import api_view
from actions.api.serializers import ActionSerializer, CommentSerializer, ReactionSerializer
from actions.models import UserAction, Comment, UserReaction, Joke
from alexa.models import User, UserActOnContent
from actstream.models import action_object_stream


class ActionViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ActionSerializer

    def get_queryset(self):
        user_id = 2     # todo move to `hard-coding`
        user = User.objects.get(id=user_id)
        circle = user.circle_set.all()[0]
        queryset = UserAction.objects.mystream(user, circle).all().order_by('-timestamp')
        return queryset


class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-created', '-id')


class ReactionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ReactionSerializer
    queryset = UserReaction.objects.all().order_by('-id')


@api_view(['POST'])
def laugh_at_joke(request):
    joke_id = request.data['joke_id']
    set_to = request.data.get('set_to', 'true').lower() != 'false'

    user_id = 2                             # todo move to `hard-coding`
    user = User.objects.get(id=user_id)
    joke = Joke.objects.get(id=joke_id)
    action = action_object_stream(joke).filter(actor_object_id=user.id)

    if set_to and action.count() < 1:
        act = UserActOnContent(user=user, verb='laughed at', object=joke)
        act.save()
    elif not set_to and action.count() > 0:
        action.delete()

    return Response({"message": "Something went wrong.."})
