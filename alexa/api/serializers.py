from rest_framework import serializers
from alexa.models import AUserMedicalState, Joke, User, UserActOnContent
from actions.models import UserAction
from rest_framework.pagination import PageNumberPagination
from actions.api.serializers import ActionSerializer
from actstream.models import action_object_stream


class ExtendedPageNumberPagination(PageNumberPagination):   # todo Move to a proper place
    max_page_size = 100
    page_size_query_param = 'page_size'


class MedicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AUserMedicalState
        fields = ('user', 'measurement', 'data', 'created', )

    data = serializers.JSONField()


class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ('id',
                  'main',
                  'punchline',
                  'user_actions', )

    user_actions = serializers.SerializerMethodField()

    def get_user_actions(self, joke: Joke):
        """
        This is the actions on the Joke object from the user in the request.

        :param joke:
        :return:
        """

        user_id = 2 # todo move to `hard-coding`
        actions = action_object_stream(joke).filter(actor_object_id=user_id)
        user_actions = UserAction.objects.all().filter(id__in=[action.id for action in actions])
        return ActionSerializer(user_actions, many=True).data


class UserActOnContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActOnContent
        fields = (
            'user',
            'verb',
            'object',
        )
