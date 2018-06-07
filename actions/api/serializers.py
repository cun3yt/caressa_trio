from rest_framework import serializers
from actions.models import UserAction, Comment, UserReaction
from caressa.settings import REST_FRAMEWORK
from alexa.models import Joke, User
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


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReaction
        fields = ('id',
                  'reaction',
                  'owner',
                  'content', )

    def create(self, validated_data):
        validated_data['owner'] = User.objects.get(id=2)    # todo: Move to `hard_codes`
        content_id = self.context['request'].parser_context['kwargs']['parent_lookup_content']
        validated_data['content'] = UserAction.objects.get(id=content_id)
        return super(ReactionSerializer, self).create(validated_data)


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('id',
                  'statement',
                  'actor',
                  'action_object_type',
                  'paginated_comments',
                  'action_object',
                  'user_reactions', )

    actor = serializers.SerializerMethodField()
    paginated_comments = serializers.SerializerMethodField()
    user_reactions = serializers.SerializerMethodField()
    action_object = GenericRelatedField({
        Joke: JokeSerializer(),
    })

    def get_actor(self, user_action: UserAction):
        user = user_action.actor
        return {
            'id': user.id,
            'profile_pic': user.get_profile_pic()
        }

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

    def get_user_reactions(self, user_action: UserAction):
        # todo IMPLEMENT THIS TO FETCH USER ACTIONS
        user_id = 2     # todo move to `hard-coding`
        reactions = user_action.action_reactions.filter(owner_id__exact=user_id).all()
        return ReactionSerializer(reactions, many=True).data
