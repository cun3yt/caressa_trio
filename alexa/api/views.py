from alexa.models import Joke, User
from rest_framework import viewsets
from rest_framework import generics
from alexa.api.serializers import JokeSerializer, ActionSerializer
from actstream.models import Action


class JokeViewSet(viewsets.ModelViewSet):
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


class ActionStreamView(generics.ListAPIView):
    serializer_class = ActionSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('id')
        user = User.objects.get(id=user_id)
        circle = user.circle_memberships.get().circle
        return Action.objects.mystream(user, circle)
