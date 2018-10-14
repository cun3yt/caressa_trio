from alexa.api.views import JokeViewSet, NewsViewSet, MedicalViewSet, UserActOnContentViewSet
from actions.api.views import ActionViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework import routers


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
    flat_router.register(r'medical-state', MedicalViewSet, 'medical-state')
    flat_router.register(r'jokes', JokeViewSet, 'joke')
    flat_router.register(r'news', NewsViewSet, 'news')
    flat_router.register(r'user-act-on-content', UserActOnContentViewSet, 'user-act-on-content')
    return flat_router
