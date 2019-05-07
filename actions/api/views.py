from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from actions.api.serializers import ActionSerializer, CommentSerializer, ReactionSerializer, QuerySerializer
from actions.models import UserAction, Comment, UserReaction, Joke, UserPost, CommentResponse, UserQuery, ActionGeneric
from alexa.models import User, UserActOnContent
from actstream.models import action_object_stream

from streaming.models import Messages
import boto3
from caressa import settings
from utilities.views.mixins import SerializerRequestViewSetMixin
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from alexa.api.permissions import IsSameUser, IsInCircle, CommentAccessible
from utilities.file_operations import download_to_tmp_from_s3, profile_picture_resizing_wrapper, upload_to_s3_from_tmp, \
    generate_versioned_picture_name


class ActionViewSet(SerializerRequestViewSetMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ActionSerializer
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        circle = user.circle_set.all()[0]
        queryset = UserAction.objects.mystream(user, circle).all().order_by('-timestamp')
        return queryset


class CommentViewSet(SerializerRequestViewSetMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, CommentAccessible)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('-created', '-id')


class ReactionViewSet(SerializerRequestViewSetMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, )    # todo: add permission to check if it is mine for deletion??
    serializer_class = ReactionSerializer
    queryset = UserReaction.objects.all().order_by('-id')


class QueryViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = QuerySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = UserQuery.objects.all().filter(user=user).order_by('-created')
        return queryset


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['PATCH'])
def select_on_action(request):
    action_generic_id = request.data['id']  # this is id of an ActionGeneric model instance

    actions = ActionGeneric.objects.all().filter(id=action_generic_id)

    if actions.count() == 0 or actions.count() > 1:
        return Response({"message": "action cannot be found"})

    action = actions[0]
    selected_key = request.date.get('selection')
    action.data["selected_key"] = selected_key

    return Response({"success": True})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def like_at_joke(request):
    joke_id = request.data['joke_id']
    set_to = request.data.get('set_to', 'true').lower() != 'false'

    user = request.user
    joke = Joke.objects.get(id=joke_id)

    action = action_object_stream(joke).filter(actor_object_id=user.id)

    if set_to and action.count() < 1:
        act = UserActOnContent(user=user, verb='laughed at', object=joke)
        act.save()
    elif not set_to and action.count() > 0:
        action.delete()

    return Response({"message": "Something went wrong.."})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def comment_response(request):
    comment_id = request.data['comment_id']
    response = request.data['response']
    user = request.user

    comment = Comment.objects.get(id=comment_id)
    content_owner = comment.content.actor   # type: User
    circle = content_owner.circle_set.all()[0]

    permission_is_in_circle = IsInCircle()
    if not permission_is_in_circle.has_object_permission(request, None, circle):
        raise PermissionDenied()

    CommentResponse(response=response, owner=user, comment_id=comment_id).save()

    return Response({"message": "Something went wrong.."})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['DELETE'])
def comment_backing_delete(request):
    comment_id = request.data['comment_id']
    user = request.user
    comment = Comment.objects.get(pk=comment_id)

    content_owner = comment.content.actor  # type: User
    circle = content_owner.circle_set.all()[0]

    permission_is_in_circle = IsInCircle()
    if not permission_is_in_circle.has_object_permission(request, None, circle):
        raise PermissionDenied()

    comment.comment_backers.remove(user)

    return Response({"message": "Something went wrong.."})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['DELETE'])
def comment_response_delete(request):
    response_id = request.data['response']

    comment_responses = CommentResponse.objects.filter(id=response_id).all()
    if comment_responses.count() == 0:
        return Response({"success": 'OK'})

    assert comment_responses.count() == 1, (
        "There must be only one comment response"
    )

    response = comment_responses[0]

    permission_is_same_user = IsSameUser()
    if not permission_is_same_user.has_object_permission(request, None, response.owner):
        raise PermissionDenied()

    CommentResponse.objects.filter(id=response_id).delete()

    return Response({"message": "Something went wrong.."})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def new_post(request):
    user = request.user

    post = UserPost(user=user, data=request.data['selections'])
    post.save()

    return Response({'message': 'Saved...'})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def pre_signed_url_for_s3(request):

    assert isinstance(request.data, list), "Invalid format of POST data."
    assert not len(request.data) > 15, "Request count cannot be higher than 15."

    lst = []
    for file_attribute_dict in request.data:
        key = file_attribute_dict['key']

        if not file_attribute_dict.get('content-type', False):
            obj = {'key': key, 'error': "URL Couldn't Not Generated, Content Type Required"}
            lst.append(obj)
            continue
        content_type = file_attribute_dict['content-type']
        request_type = file_attribute_dict.get('request-type', 'PUT')
        client_method = file_attribute_dict.get('client-method', 'put_object')
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

        obj = {
            'key': key,
            'url': url
        }
        lst.append(obj)

    return Response(lst)


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def new_job_for_message_queue(request):
    user = request.user
    message_type = request.data.get('type')
    message_key = request.data.get('key')
    content_str = 'content'

    if content_str in request.data:
        content = request.data['content']
    else:
        content = ''

    message = {
        'user': user.id,
        'message_type': message_type,
        'key': message_key,
        'content': content
    }
    new_message = Messages(message=message)
    new_message.save()

    return Response({'message': 'Saved...'})


@authentication_classes((OAuth2Authentication, ))
@permission_classes((IsAuthenticated, ))
@api_view(['POST'])
def new_profile_picture(request):
    user = request.user
    file_name = request.data.get('file_name')

    current_user_profile_pic = user.profile_pic

    new_profile_pic_hash_version = generate_versioned_picture_name(current_user_profile_pic)

    download_to_tmp_from_s3(file_name, settings.S3_RAW_UPLOAD_BUCKET)

    save_picture_format = 'jpg'
    picture_set = profile_picture_resizing_wrapper(file_name, new_profile_pic_hash_version, save_picture_format)
    upload_to_s3_from_tmp(settings.S3_PRODUCTION_BUCKET, picture_set, 'user', user.id)

    user.profile_pic = new_profile_pic_hash_version.rsplit('.')[0]
    user.save()

    return Response({'message': 'Profile Picture Updated'})