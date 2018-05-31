from rest_framework import viewsets
from rest_framework.response import Response
from alexa.api.serializers import MedicalStateSerializer, JokeSerializer
from alexa.models import AUserMedicalState, Joke


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
            exclusion_list = [int(x) for x in request.query_params.get('exclude', '').split(',') if len(x) > 0]
            joke = Joke.fetch_random(exclusion_list)
            serializer = JokeSerializer(joke)
            return Response(serializer.data)
        else:
            return super(JokeViewSet, self).retrieve(request, args, kwargs)
