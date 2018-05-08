from rest_framework import serializers
from alexa.models import Joke


class JokeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Joke
        fields = ('main', 'punchline', )
