from rest_framework import viewsets
from alexa.api.serializers import MedicalStateSerializer
from alexa.models import AUserMedicalState


class MedicalViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalStateSerializer

    def get_queryset(self):
        measurement_type = self.request.query_params.get('m-type')
        return AUserMedicalState.objects.filter(measurement__exact=measurement_type).order_by('created').all()
