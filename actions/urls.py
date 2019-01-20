from actions.api.views import ActionViewSet, CommentViewSet, ReactionViewSet
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework import routers


def register_nested_routes(router: ExtendedSimpleRouter):
    action_router = router.register(r'actions',
                                    ActionViewSet,
                                    base_name='action', )
    action_router.register(r'comments',
                           CommentViewSet,
                           base_name='actions-comment',
                           parents_query_lookups=['content'], )
    action_router.register(r'reactions',
                           ReactionViewSet,
                           base_name='actions-reaction',
                           parents_query_lookups=['content'], )
    return router


def register_flat_routes(flat_router: routers):
    flat_router.register(r'streams', ActionViewSet, 'stream')       # todo: Check if dead!
    flat_router.register(r'comments', CommentViewSet, 'comment')    # todo: Check if dead!
    return flat_router
