from rest_framework import serializers
from alexa.models import AUserMedicalState
from rest_framework.pagination import PageNumberPagination


class ExtendedPageNumberPagination(PageNumberPagination):   # todo Move to a proper place
    max_page_size = 100
    page_size_query_param = 'page_size'


class MedicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AUserMedicalState
        fields = ('user', 'measurement', 'data', 'created', )

    data = serializers.JSONField()
