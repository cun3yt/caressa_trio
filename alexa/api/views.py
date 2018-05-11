from alexa.models import Joke, User
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from alexa.api.serializers import JokeSerializer, ActionSerializer
from actstream.models import Action


class JokeViewSet(viewsets.ModelViewSet):
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


@api_view(http_method_names=['GET'])
def action_stream(request: Request) -> Response:
    user_id = request.query_params.get('id')
    user = User.objects.get(id=user_id)
    circle = user.circle_memberships.get().circle
    streams = Action.objects.mystream(user, circle)
    serializer = ActionSerializer(streams, many=True)
    return Response(serializer.data)
