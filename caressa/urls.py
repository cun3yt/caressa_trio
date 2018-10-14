"""https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from alexa.views import main_view, alexa_io
from streaming.views import stream_io_wrapper, playlist_replication
from actions.api.views import ActionViewSet, CommentViewSet, ReactionViewSet, laugh_at_joke, find_interesting_at_news, \
    new_post, pre_signed_url_for_s3, new_job_for_message_queue, personalize_content
from alexa.api.views import MedicalViewSet, JokeViewSet, NewsViewSet, UserActOnContentViewSet
from actions.api.views import laugh_at_joke, find_interesting_at_news, \
    new_post

from actions.urls import register_nested_routes as register_nested_action_urls, \
    register_flat_routes as register_flat_action_routes
from alexa.urls import register_nested_routes as register_nested_alexa_urls, \
    register_flat_routes as register_flat_alexa_routes

from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter
from voice_service.views import speech_to_text
from caressa.admin import get_admin


admin = get_admin()

router = ExtendedSimpleRouter()
router = register_nested_action_urls(router)
router = register_nested_alexa_urls(router)

flat_router = routers.DefaultRouter()
flat_router = register_flat_action_routes(flat_router)
flat_router = register_flat_alexa_routes(flat_router)


urlpatterns = [
    path('', main_view),
    path('act/', include(router.urls)),
    path('flat-api/', include(flat_router.urls)),
    path('admin/', admin.site.urls),
    path('discussion', alexa_io),
    path('streaming', stream_io_wrapper),
    path('speech-to-text', speech_to_text),
    path('replicate/', playlist_replication),
    path('api-auth/', include('rest_framework.urls')),
    path('laugh/', laugh_at_joke),
    path('find-interesting/', find_interesting_at_news),
    path('post/', new_post),
    path('generate_signed_url/', pre_signed_url_for_s3),
    path('new_message/', new_job_for_message_queue),
    path('personalize/', personalize_content),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
