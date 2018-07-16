from datetime import datetime
from rest_framework import serializers
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


class Comment(object):
    def __init__(self, email, content, created=None):
        self.email = email
        self.content = content
        self.created = created or datetime.now()


class CommentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    content = serializers.CharField(max_length=200)
    created = serializers.DateTimeField()

    def create(self, validated_data):
        return Comment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.content = validated_data.get('content', instance.content)
        instance.created = validated_data.get('created', instance.created)
        instance.save()
        return instance


comment = Comment(email='leila@example.com', content='foo bar')
serializer = CommentSerializer(comment)

json = JSONRenderer().render(serializer.data)

stream = BytesIO(json)
data = JSONParser().parse(stream)

data["email"] = 'sample@example.com'
seriall = CommentSerializer(comment, data=data)
if seriall.is_valid():
    seriall.save()
