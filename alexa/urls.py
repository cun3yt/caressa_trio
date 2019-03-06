from alexa.api.views import JokeViewSet, NewsViewSet, UserMeViewSet, SeniorListViewSet, \
    ChannelsViewSet, CirclesViewSet, UserSettingsViewSet, CircleInvitationViewSet
from actions.api.views import ActionViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework import routers
from django.urls import path

from alexa.views import circle_member_invitation


def register_nested_routes(router: ExtendedSimpleRouter):
    joke_router = router.register(r'jokes',
                                  JokeViewSet,
                                  base_name='joke', )
    joke_router.register(r'actions',
                         ActionViewSet,
                         base_name='action',
                         parents_query_lookups=['action_object_object_id'], )

    news_router = router.register(r'news',
                                  NewsViewSet,
                                  base_name='news')
    news_router.register(r'actions',
                         ActionViewSet,
                         base_name='action',
                         parents_query_lookups=['action_object_object_id'], )
    return router


def register_flat_routes(flat_router: routers):
    flat_router.register(r'jokes', JokeViewSet, 'joke')
    flat_router.register(r'news', NewsViewSet, 'news')
    return flat_router


def individual_paths():
    api_url_list = [
        path('api/users/me/', UserMeViewSet.as_view({'get': 'retrieve'})),
        path('api/users/me/circles/', CirclesViewSet.as_view({'get': 'retrieve'})),
        path('api/circles/<int:circle_pk>/members/', CircleInvitationViewSet.as_view({'post': 'create', })),
        path('api/users/me/channels/', ChannelsViewSet.as_view({'get': 'retrieve'})),
        path('api/users/<int:user_pk>/settings/', UserSettingsViewSet.as_view({'get': 'retrieve',
                                                                               'patch': 'partial_update', })),
        path('api/seniors/', SeniorListViewSet.as_view({'get': 'list',
                                                       'post': 'create', })),
        path('api/seniors/<int:pk>/', SeniorListViewSet.as_view({'delete': 'destroy',
                                                                 'put': 'update'})),
    ]

    web_url_list = [
        path('circle-invitation/', circle_member_invitation, name='circle-member-invitation'),
    ]
    return api_url_list + web_url_list
