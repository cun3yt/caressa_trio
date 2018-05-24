from rest_framework import serializers
from actions.models import UserAction, Comment
from caressa.settings import REST_FRAMEWORK


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'comment', )


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAction
        fields = ('id',
                  'statement',
                  'action_object_type',
                  'paginated_comments')

    paginated_comments = serializers.SerializerMethodField()

    def get_paginated_comments(self, user_action: UserAction):
        page_size = REST_FRAMEWORK.get('PAGE_SIZE', 5)
        comments = user_action.action_comments.all()[:page_size]

        return {
            'count': user_action.number_of_comments,
            'next': {'page': 2} if user_action.number_of_comments > page_size else None,
            'previous': None,
            'results': CommentSerializer(comments, many=True).data,
        }
