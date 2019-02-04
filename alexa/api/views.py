from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utilities.views.mixins import SerializerRequestViewSetMixin
from alexa.api.serializers import UserSerializer, SeniorSerializer, MedicalStateSerializer, JokeSerializer, \
    NewsSerializer, ChannelSerializer, CircleSerializer
from alexa.models import AUserMedicalState, Joke, News, User, Circle
from alexa.api.permissions import IsSameUser, IsFacilityMember, IsInCircle
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.pagination import PageNumberPagination


class UserMeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSameUser, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class CirclesViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsInCircle, )
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def get_object(self):
        return self.request.user.circle_set.all()[0]


class ChannelsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    queryset = User.objects.all()
    serializer_class = ChannelSerializer

    def get_object(self):
        return self.request.user


class SeniorListViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsFacilityMember, )    # todo facility admin only check is needed
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


class MedicalViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = MedicalStateSerializer

    def get_queryset(self):
        measurement_type = self.request.query_params.get('m-type')
        senior = self.request.user.circle_set.all()[0].person_of_interest
        return AUserMedicalState.objects.filter(user=senior,
                                                measurement__exact=measurement_type).order_by('created').all()


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


class NewsViewSet(SerializerRequestViewSetMixin, viewsets.ReadOnlyModelViewSet):
    authentication_classes = (OAuth2Authentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = NewsSerializer
    queryset = News.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] == '0':
            news = self.fetch_random_news(request)
            serializer = NewsSerializer(news, context={'request': request})
            return Response(serializer.data)
        else:
            return super(NewsViewSet, self).retrieve(request, args, kwargs)

    @classmethod
    def fetch_random_news(cls, request):
        exclusion_list = [
            int(x) for x
            in request.query_params.get('exclude', '').split(',')
            if len(x) > 0
        ]
        return News.fetch_random(exclusion_list)
