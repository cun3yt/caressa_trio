from django.urls import path
from streaming.api.views import UserContentRepositoryViewSet


api_urls = [
    path('api/users/me/user-content-repository/',
         UserContentRepositoryViewSet.as_view({
             'get': 'retrieve',
             'patch': 'partial_update',
         })),
]
