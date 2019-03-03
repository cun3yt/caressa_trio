from alexa.api.views import JokeViewSet, NewsViewSet, UserMeViewSet, SeniorListViewSet, \
    ChannelsViewSet, CirclesViewSet, UserSettingsViewSet
from actions.api.views import ActionViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework import routers
from django.urls import path


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
    lst = [
        path('api/users/me/', UserMeViewSet.as_view({'get': 'retrieve'})),
        path('api/users/me/circles/', CirclesViewSet.as_view({'get': 'retrieve'})),
        path('api/users/me/channels/', ChannelsViewSet.as_view({'get': 'retrieve'})),
        path('api/users/<int:user_pk>/settings/', UserSettingsViewSet.as_view({'get': 'retrieve',
                                                                               'patch': 'partial_update', })),
        path('api/seniors/', SeniorListViewSet.as_view({'get': 'list',
                                                       'post': 'create', })),
        path('api/seniors/<int:pk>/', SeniorListViewSet.as_view({'delete': 'destroy',
                                                                 'put': 'update'})),
    ]

    return lst
