from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from streaming.api.permissions import UserWithInjectedContentRepository
from streaming.api.serializers import UserContentRepositorySerializer
from streaming.models import UserContentRepository


class UserContentRepositoryViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, UserWithInjectedContentRepository, )
    queryset = UserContentRepository.objects.all()
    serializer_class = UserContentRepositorySerializer

    def get_object(self):
        return UserContentRepository.get_for_user(self.request.user)
