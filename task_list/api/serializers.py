from task_list.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


# class TaskSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = CaretakerTask
#         fields = ('id', 'caretaker', 'title', 'details',
#                   'ideal_time_to_do', 'done_time', 'assigned_to')
#
#
# class CaretakerSerializer(serializers.HyperlinkedModelSerializer):
#     # user = serializers.HyperlinkedIdentityField(
#     #     many=False,
#     #     read_only=True,
#     #     view_name='user-detail'
#     # )
#
#     tasks = TaskSerializer
#
#     class Meta:
#         model = Caretaker
#         fields = ('gender', 'birth_date', 'tasks')
#         # fields = ('user', 'gender', 'birth_date', 'circle', 'tasks')
