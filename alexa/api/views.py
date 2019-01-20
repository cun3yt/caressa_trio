from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from alexa.api.serializers import UserSerializer, SeniorSerializer, MedicalStateSerializer, JokeSerializer, NewsSerializer, UserActOnContentSerializer
from alexa.models import AUserMedicalState, Joke, News, UserActOnContent, User
from alexa.api.permissions import IsSameUser
from oauth2_provider.contrib.rest_framework import OAuth2Authentication


class UserMeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, IsSameUser, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SeniorListViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = SeniorSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_provider():
            return []
        queryset = User.objects.filter(user_type__exact=User.CARETAKER,
                                       senior_living_facility=user.senior_living_facility).all()
        return queryset


class MedicalViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalStateSerializer

    def get_queryset(self):
        measurement_type = self.request.query_params.get('m-type')
        return AUserMedicalState.objects.filter(measurement__exact=measurement_type).order_by('created').all()


class JokeViewSet(viewsets.ModelViewSet):
    serializer_class = JokeSerializer
    queryset = Joke.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] == '0':
            joke = self.fetch_random_joke(request)
            serializer = JokeSerializer(joke)
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


class NewsViewSet(viewsets.ModelViewSet):
    serializer_class = NewsSerializer
    queryset = News.objects.all()

    def retrieve(self, request, *args, **kwargs):
        if kwargs['pk'] == '0':
            news = self.fetch_random_news(request)
            serializer = NewsSerializer(news)
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


class UserActOnContentViewSet(viewsets.ModelViewSet):
    serializer_class = UserActOnContentSerializer
    queryset = UserActOnContent.objects.all()
