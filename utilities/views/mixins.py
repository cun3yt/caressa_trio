from django.contrib.auth import get_user_model
from rest_framework import serializers

from caressa.settings import S3_REGION, S3_PRODUCTION_BUCKET


class SerializerRequestViewSetMixin:
    def get_serializer_context(self):
        return {
            'request': self.request
        }


class ForAdminApplicationMixin:  # Temporary For End Point Coordination With the Remote Office
    pass
