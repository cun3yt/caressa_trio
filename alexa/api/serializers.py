from rest_framework import serializers
from alexa.models import Joke


class JokeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Joke
        fields = ('main', 'punchline', )


class ActionSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'statement': instance.__str__(),
            'action_object_type': type(instance.action_object).__name__ if instance.action_object else None,
            'action_object': JokeSerializer(instance.action_object).data
            if instance.action_object and isinstance(instance.action_object, Joke) else None,
        }

    def create(self, validated_data):
        pass

    def save(self, **kwargs):
        pass

    def to_internal_value(self, data):
        pass
