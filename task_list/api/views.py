from django.utils import timezone
import datetime
from task_list.models import User
from rest_framework import viewsets
from task_list.api.serializers import UserSerializer


# class TaskViewSet(viewsets.ModelViewSet):
#     serializer_class = TaskSerializer
#
#     def get_queryset(self):
#         queryset = CaretakerTask.objects.all()
#         if self.request.query_params.get('time', None) == 'today':
#             now = timezone.now()
#             queryset = queryset.filter(ideal_time_to_do__range=(now, now + datetime.timedelta(days=1)))
#         return queryset.order_by('-ideal_time_to_do')
#
#     def perform_update(self, serializer):
#         serializer.instance.done_time = timezone.now()
#         serializer.save()
#
#
# class CaretakerViewSet(viewsets.ModelViewSet):
#     queryset = Caretaker.objects.all()
#     serializer_class = CaretakerSerializer
#
#
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
