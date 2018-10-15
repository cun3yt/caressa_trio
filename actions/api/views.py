from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import api_view
from actions.api.serializers import ActionSerializer, CommentSerializer, ReactionSerializer
from actions.models import UserAction, Comment, UserReaction, Joke, News, UserPost, Song
from alexa.models import User, UserActOnContent
from actstream.models import action_object_stream
from streaming.models import Messages
import boto3
from caressa import settings


class ActionViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ActionSerializer

    def get_queryset(self):
        user_id = 2     # todo move to `hard-coding`
        user = User.objects.get(id=user_id)
        circle = user.circle_set.all()[0]
        queryset = UserAction.objects.mystream(user, circle).all().order_by('-timestamp')
        return queryset


class CommentViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-created', '-id')


class ReactionViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ReactionSerializer
    queryset = UserReaction.objects.all().order_by('-id')


@api_view(['POST'])
def laugh_at_joke(request):
    joke_id = request.data['joke_id']
    set_to = request.data.get('set_to', 'true').lower() != 'false'

    user_id = 2                             # todo move to `hard-coding`
    user = User.objects.get(id=user_id)
    joke = Joke.objects.get(id=joke_id)
    action = action_object_stream(joke).filter(actor_object_id=user.id)

    if set_to and action.count() < 1:
        act = UserActOnContent(user=user, verb='laughed at', object=joke)
        act.save()
    elif not set_to and action.count() > 0:
        action.delete()

    return Response({"message": "Something went wrong.."})


@api_view(['POST'])
def find_interesting_at_news(request):
    news_id = request.data['news_id']
    set_to = request.data.get('set_to', 'true').lower() != 'false'

    user_id = 2                             # todo move to `hard-coding`
    user = User.objects.get(id=user_id)
    news = News.objects.get(id=news_id)
    action = action_object_stream(news).filter(actor_object_id=user.id)

    if set_to and action.count() < 1:
        act = UserActOnContent(user=user, verb='found interesting', object=news)
        act.save()
    elif not set_to and action.count() > 0:
        action.delete()

    return Response({"message": "Something went wrong.."})


@api_view(['POST'])
def like_the_song(request):
    song_id = request.data.get('song_id')
    set_to = request.data.get('set_to', 'true').lower() != 'false'

    user_id = 2                             # todo move to `hard-coding`
    user = User.objects.get(id=user_id)
    song = Song.objects.get(id=song_id)
    action = action_object_stream(song).filter(actor_object_id=user.id)

    if set_to and action.count() < 1:
        act = UserActOnContent(user=user, verb='liked', object=song)
        act.save()
    elif not set_to and action.count() > 0:
        action.delete()

    return Response({"message": "Something went wrong.."})


@api_view(['POST'])
def new_post(request):
    user_id = 2  # todo move to `hard-coding`
    user = User.objects.get(id=user_id)

    post = UserPost(user=user, data=request.data['selections'])
    post.save()

    return Response({'message': 'Saved...'})


@api_view(['POST'])
def pre_signed_url_for_s3(request):
    key = request.data['key']
    content_type = request.data['content-type']
    request_type = request.data['request-type']
    client_method = request.data['client-method']
    s3 = boto3.client('s3')

    url = s3.generate_presigned_url(
        ClientMethod=client_method,
        Params={
            'Bucket': settings.S3_RAW_UPLOAD_BUCKET,
            'Key': key,
            'ContentType': content_type
        },
        HttpMethod=request_type
    )
    return Response(url)


@api_view(['POST'])
def new_job_for_message_queue(request):
    user_id = 2
    message_type = request.data['type']
    message_key = request.data['key']
    key = 'content'

    if key in request.data:
        content = request.data['content']['text'][0]
    else:
        content = ''

    message = {
        'user': user_id,
        'message_type': message_type,
        'key': message_key,
        'content': content
    }
    new_message = Messages(message=message)
    new_message.save()

    return Response({'message': 'Saved...'})


@api_view(['POST'])
def personalize_content(request):
    user_id = 2
    message_type = request.data['type']
    message_list = request.data['list']

    message = {
        'user': user_id,
        'message_type': message_type,
        'list': message_list,
    }
    new_message = Messages(message=message)
    new_message.save()

    return Response({'message': 'Saved...'})
