from rest_framework import serializers
from streaming.models import UserContentRepository, AudioFile


class UserContentRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContentRepository
        fields = ('injected_content_repository', 'created', 'modified', )
        read_only_fields = ('created', 'modified', )

    injected_content_repository = serializers.JSONField()


class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ('audio_type', 'url', 'hash', )
        read_only_fields = ('hash', )
