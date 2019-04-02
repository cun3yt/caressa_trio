from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utilities.views.mixins import SerializerRequestViewSetMixin
from alexa.models import Joke, User, UserSettings, Circle, CircleInvitation
from alexa.api.serializers import UserSerializer, SeniorSerializer, JokeSerializer, \
    ChannelSerializer, CircleSerializer, UserSettingsSerializer, CircleInvitationSerializer, \
    CircleReinvitationSerializer
from alexa.api.permissions import IsSameUser, IsFacilityOrgMemberAndCanSeeSenior, IsInCircle, CanAccessUserSettings
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.pagination import PageNumberPagination


class UserMeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSameUser, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserSettingsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, CanAccessUserSettings, )     # todo make this work!
    queryset = UserSettings.objects.all()
    serializer_class = UserSettingsSerializer

    def get_object(self):
        user_pk = self.kwargs.get('user_pk')
        user = User.objects.get(pk=user_pk)
        settings, _ = UserSettings.objects.get_or_create(user=user, defaults={})
        return settings


class CirclesViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsInCircle, )
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def get_object(self):
        return self.request.user.circle_set.all()[0]


class CircleInvitationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsInCircle, )
    serializer_class = CircleInvitationSerializer

    def get_queryset(self):
        return CircleInvitation.objects.filter(converted_user_id__isnull=True).all()


class CircleReinvitationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated, IsInCircle,)
    queryset = CircleInvitation.objects.all()
    serializer_class = CircleReinvitationSerializer


class ChannelsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()
    serializer_class = ChannelSerializer

    def get_object(self):
        return self.request.user


class SeniorListViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin,
                        mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityOrgMemberAndCanSeeSenior, )
    serializer_class = SeniorSerializer

    class _Pagination(PageNumberPagination):
        max_page_size = 10000
        page_size_query_param = 'page_size'
        page_size = 10000

    pagination_class = _Pagination

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def get_queryset(self):
        user = self.request.user
        if not user.is_provider():
            return []
        queryset = User.objects.filter(user_type__exact=User.CARETAKER,
                                       senior_living_facility=user.senior_living_facility,
                                       is_active=True).all()
        return queryset     # todo page size needs to be adjusted...


class JokeViewSet(SerializerRequestViewSetMixin, viewsets.ReadOnlyModelViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = JokeSerializer
    queryset = Joke.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] == '0':
            joke = self.fetch_random_joke(request)
            serializer = JokeSerializer(joke, context={'request': request})
            return Response(serializer.data)
        else:
            return super(JokeViewSet, self).retrieve(request, args, kwargs)

    @classmethod
    def fetch_random_joke(cls, request):
        exclusion_list = [
            int(x) for x
            in request.query_params.get('exclude', '').split(',')
            if len(x) > 0
        ]
        return Joke.fetch_random(exclusion_list)
