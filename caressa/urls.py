"""caressa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from alexa.views import main_view, alexa_io
from actions.api.views import ActionViewSet, CommentViewSet, ReactionViewSet, laugh_at_joke
from alexa.api.views import MedicalViewSet, JokeViewSet, UserActOnContentViewSet
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter


router = ExtendedSimpleRouter()

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

joke_router = router.register(r'jokes',
                              JokeViewSet,
                              base_name='joke', )
joke_router.register(r'actions',
                     ActionViewSet,
                     base_name='action',
                     parents_query_lookups=['action_object_object_id'], )

flat_router = routers.DefaultRouter()
flat_router.register(r'streams', ActionViewSet, 'stream')
flat_router.register(r'comments', CommentViewSet, 'comment')
flat_router.register(r'medical-state', MedicalViewSet, 'medical-state')
flat_router.register(r'jokes', JokeViewSet, 'joke')
flat_router.register(r'user-act-on-content', UserActOnContentViewSet, 'user-act-on-content')

urlpatterns = [
    path('', main_view),
    path('discussion', alexa_io),
    path('act/', include(router.urls)),
    path('flat-api/', include(flat_router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('laugh/', laugh_at_joke),
]
