from rest_framework import serializers
from actions.models import UserAction, Comment, UserReaction, UserPost, CommentResponse, UserQuery
from caressa.settings import REST_FRAMEWORK, SUPPORT_EMAIL_ACCOUNTS
from alexa.models import Joke, User, News, Song
from generic_relations.relations import GenericRelatedField
from django.db.utils import IntegrityError
from utilities.email import send_email



class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ('id', 'main', 'punchline')


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id', 'headline', 'content')


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ('id', 'title', 'artist', 'duration', 'genre', 'file_name')


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = ('id', 'message', 'reply_message', 'solve_date')

    message = serializers.SerializerMethodField()

    def create(self, validated_data):
        user = self.context['request'].user
        message = {
            'title': self.context['request'].data['title'],
            'main': self.context['request'].data['main']
        }
        validated_data['user'] = User.objects.get(id=user.id)
        validated_data['message'] = message
        send_email(SUPPORT_EMAIL_ACCOUNTS,
                   'New Support Request From {}'.format(user.full_name),
                   'email/support-request.html',
                   'email/support-request.txt',
                   context={
                       'user_full_name': user.full_name,
                       'user_mail': user.email
                   })
        return super(QuerySerializer, self).create(validated_data)

    def get_message(self, user_query: UserQuery):
            data = {
                'title': user_query.message['title'],
                'main': user_query.message['main']
            }
            return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'comment', 'created', 'comment_backers', 'responses')

    comment_backers = serializers.SerializerMethodField()
    responses = serializers.SerializerMethodField()

    def get_responses(self, comment: Comment):
        comment_responses = CommentResponse.objects.filter(comment_id=comment.id)
        response_list = [{
                'id': response.id,
                'response': response.response,
                'created': response.created,
                'full_name': response.owner.get_full_name(),
                'profile_pic': response.owner.get_profile_pic(),
            } for response in comment_responses]
        return response_list

    def get_if_user_backed_the_comment(self, comment_id):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        comment = Comment.objects.get(pk=comment_id)
        return comment.comment_backers.filter(id=user.id) if user else []

    def get_comment_backers(self, comment: Comment):
        user_backed_qs = self.get_if_user_backed_the_comment(comment.id)
        did_user_backed = user_backed_qs.exists()
        backers = comment.comment_backers.all()
        backer_list = [{
            'full_name': backer.get_full_name(),
            'profile_pic': backer.get_profile_pic()
        } for backer in backers]
        return {
            'did_user_backed': did_user_backed,
            'all_backers': backer_list
        }

    def create(self, validated_data):
        backer_instance = self.context['request'].user
        validated_data['comment_backers'] = [backer_instance, ]
        content_id = self.context['request'].parser_context['kwargs']['parent_lookup_content']
        validated_data['content'] = UserAction.objects.get(id=content_id)
        new_comment = validated_data['comment']
        comments_qs = Comment.objects.filter(comment=new_comment)   # todo What happens if the same comment exists in another circle?
        if not comments_qs.exists():
            return super(CommentSerializer, self).create(validated_data)
        try:
            comments_qs[0].comment_backers.add(backer_instance)
        except IntegrityError:
            pass  # todo returns unique key errors with same comment_id, user_id pair
        return comments_qs[0]


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReaction
        fields = ('id',
                  'reaction',
                  'owner_profile',
                  'content', )

    owner_profile = serializers.SerializerMethodField()

    def get_owner_profile(self, user_reaction: UserReaction, ):
        owner_profile = {
            'full_name': user_reaction.owner.get_full_name(),
            'profile_pic': user_reaction.owner.get_profile_pic()
        }
        return owner_profile

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['owner'] = User.objects.get(id=user.id)
        content_id = self.context['request'].parser_context['kwargs']['parent_lookup_content']
        validated_data['content'] = UserAction.objects.get(id=content_id)
        return super(ReactionSerializer, self).create(validated_data)


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = ('id',
                  'content', )

    content = serializers.SerializerMethodField()

    @staticmethod
    def get_content(user_post: UserPost):
        return str(user_post)


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
        News: NewsSerializer(),
        UserPost: UserPostSerializer(),
        Song: SongSerializer(),
    })

    def get_actor(self, user_action: UserAction):
        user = user_action.actor
        return {
            'id': user.id,
            'profile_pic': user.get_profile_pic()
        }

    @property
    def context_to_nested_serializers(self):
        request = self.context.get('request')
        context = {} if request is None else {'request': request}
        return context

    def get_paginated_comments(self, user_action: UserAction):
        page_size = REST_FRAMEWORK.get('PAGE_SIZE', 5)
        comments = user_action.action_comments.order_by('-created').all()[:page_size]

        return {
            'count': user_action.number_of_comments,
            'next': 'http://{base}/act/actions/{id}/comments/?page=2'.format(
                base=self.context['request'].META['HTTP_HOST'],
                id=user_action.id) if user_action.number_of_comments > page_size else None,
            'previous': None,
            'results': CommentSerializer(comments,
                                         context=self.context_to_nested_serializers,
                                         many=True).data,
        }

    def get_if_user_liked_the_action(self, action_id):
        user = self.context['request'].user
        return UserReaction.objects.filter(content_id=action_id, owner=user)

    def get_user_reactions(self, user_action: UserAction):
        action_id = user_action.id
        reactions = UserReaction.objects.filter(content_id=action_id).order_by('-created')
        serialized_reactions = ReactionSerializer(reactions,
                                                  context=self.context_to_nested_serializers,
                                                  many=True).data

        user_like_qs = self.get_if_user_liked_the_action(action_id)
        did_user_like = user_like_qs.exists()
        user_reaction_id = user_like_qs[0].id if did_user_like else None

        return {
            'user_like_state': {'did_user_like': did_user_like, 'reaction_id': user_reaction_id},
            'all_likes':
                {
                    'total': len(serialized_reactions),
                    'to_be_shown': serialized_reactions[:3]
                }
        }
