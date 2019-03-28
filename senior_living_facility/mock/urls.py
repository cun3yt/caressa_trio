from django.urls import path

from senior_living_facility.api.views import MessageThreadMessagesViewSet
from senior_living_facility.mock.views import message_thread, user_profile

mock_urls = [
    path('api/users/<int:pk>/', user_profile, name='user_profile',),
    path('api/message-threads/<int:pk>/', message_thread, name='mock_message_thread',),
    path('api/message-threads/<int:pk>/messages/',
         MessageThreadMessagesViewSet.as_view({'get': 'list', })),
]
