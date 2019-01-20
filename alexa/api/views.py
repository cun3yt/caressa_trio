from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from alexa.api.serializers import MedicalStateSerializer, JokeSerializer, NewsSerializer
from alexa.models import AUserMedicalState, Joke, News
from utilities.views.mixins import SerializerRequestViewSetMixin
from oauth2_provider.contrib.rest_framework import OAuth2Authentication


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
