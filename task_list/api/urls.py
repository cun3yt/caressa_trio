from django.conf.urls import url, include
from rest_framework import routers
from task_list.api import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
# router.register(r'caretakers', views.CaretakerViewSet)
# router.register(r'tasks', views.TaskViewSet, base_name='caretakertask')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
