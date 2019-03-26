"""
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
from alexa.views import main_view
from streaming.views import stream_io_wrapper

from actions.urls import register_nested_routes as register_nested_action_urls, \
    register_flat_routes as register_flat_action_routes
from alexa.urls import register_nested_routes as register_nested_alexa_urls, \
    register_flat_routes as register_flat_alexa_routes
from alexa.urls import individual_paths as individual_paths_alexa

from actions.api.views import like_at_joke, like_at_news, comment_response, new_post, pre_signed_url_for_s3, \
    new_job_for_message_queue, comment_response_delete, comment_backing_delete, new_profile_picture
from rest_framework import routers
from rest_framework_extensions.routers import ExtendedSimpleRouter
from voice_service.views import speech_to_text
from caressa.admin import get_admin
from senior_living_facility.urls import urls as senior_living_facility_urls, \
    api_urls as senior_living_facility_api_urls
from streaming.urls import api_urls as streaming_api_urls


from rest_framework.documentation import include_docs_urls

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
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('flat-api/', include(flat_router.urls)),
    path('admin/', admin.site.urls),
    path('streaming', stream_io_wrapper),
    path('speech-to-text', speech_to_text),
    path('api-auth/', include('rest_framework.urls')),
    path('like_joke/', like_at_joke),
    path('like_news/', like_at_news),
    path('comment_response/', comment_response),
    path('comment_response_delete/', comment_response_delete),
    path('comment_backing_delete/', comment_backing_delete),
    path('post/', new_post),
    path('generate_signed_url/', pre_signed_url_for_s3),
    path('new_message/', new_job_for_message_queue),
    path('new_profile_picture/', new_profile_picture),
    path('accounts/', include(senior_living_facility_urls)),
    path('docs/', include_docs_urls(title='Caressa API',
                                    public=True,
                                    authentication_classes=[],
                                    permission_classes=[], ))
]

urlpatterns += individual_paths_alexa() + senior_living_facility_api_urls
urlpatterns += streaming_api_urls
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
