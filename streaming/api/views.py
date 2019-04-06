from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from streaming.api.permissions import UserWithInjectedContentRepository
from streaming.api.serializers import UserContentRepositorySerializer, AudioFileSerializer
from streaming.models import UserContentRepository, AudioFile, UserAudioFileSignal


class UserContentRepositoryViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, UserWithInjectedContentRepository, )
    queryset = UserContentRepository.objects.all()
    serializer_class = UserContentRepositorySerializer

    def get_object(self):
        return UserContentRepository.get_for_user(self.request.user)


class UserAudioFileSignalsViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Purpose: To serve a given user's liked (or yes-answer'ed) audio files
    """

    authentication_classes = (OAuth2Authentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = AudioFileSerializer
    queryset = AudioFile.objects.all()

    @property
    def audio_file(self):
        hash_ = self.request.data.get('hash')
        return AudioFile.objects.get(hash=hash_)

    def create(self, request, *args, **kwargs):
        signal_type = self.request.data.get('signal')
        signal_type = signal_type if UserAudioFileSignal.is_signal_valid(signal_type) \
            else UserAudioFileSignal.SIGNAL_POSITIVE
        reaction = self.audio_file.add_to_positive_negative_signal_by(user=request.user,
                                                                      signal_type=signal_type)
        serializer = AudioFileSerializer(reaction.audio_file, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
