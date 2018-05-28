from rest_framework import serializers
from actions.models import UserAction, Comment
from caressa.settings import REST_FRAMEWORK
from alexa.models import Joke, User
from actions.models import UserAction
from generic_relations.relations import GenericRelatedField


class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ('id', 'main', 'punchline')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'comment', 'created', 'commenter', )

    commenter = serializers.SerializerMethodField()

    def get_commenter(self, comment: Comment):
        return comment.owner.get_full_name()

    def create(self, validated_data):
        validated_data['owner'] = User.objects.get(id=2)    # todo: Move to `hard_codes`
        content_id = self.context['request'].parser_context['kwargs']['parent_lookup_content']
        validated_data['content'] = UserAction.objects.get(id=content_id)
        return super(CommentSerializer, self).create(validated_data)


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('id',
                  'statement',
                  'action_object_type',
                  'paginated_comments',
                  'data',
                  'action_object', )

    paginated_comments = serializers.SerializerMethodField()
    data = serializers.JSONField()
    action_object = GenericRelatedField({
        Joke: JokeSerializer(),
    })

    def get_paginated_comments(self, user_action: UserAction):
        page_size = REST_FRAMEWORK.get('PAGE_SIZE', 5)
        comments = user_action.action_comments.order_by('-created').all()[:page_size]

        return {
            'count': user_action.number_of_comments,
            'next': 'http://{base}/act/actions/{id}/comments/?page=2'.format(
                base=self.context['request'].META['HTTP_HOST'],
                id=user_action.id) if user_action.number_of_comments > page_size else None,
            'previous': None,
            'results': CommentSerializer(comments, many=True).data,
        }
