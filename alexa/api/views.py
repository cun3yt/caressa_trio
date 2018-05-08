from alexa.models import Joke
from rest_framework import viewsets
from alexa.api.serializers import JokeSerializer


class JokeViewSet(viewsets.ModelViewSet):
    queryset = Joke.objects.all()
    serializer_class = JokeSerializer
