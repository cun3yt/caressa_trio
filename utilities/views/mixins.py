from rest_framework import serializers


class SerializerRequestViewSetMixin:
    def get_serializer_context(self):
        return {
            'request': self.request
        }


class MockStatusMixin(serializers.Serializer):  # Temporary For End Point Coordination With the Remote Office
    mock_status = serializers.SerializerMethodField()

    @staticmethod
    def get_mock_status(obj):
        return True


class ForAdminMixin:  # Temporary For End Point Coordination With the Remote Office
    pass
