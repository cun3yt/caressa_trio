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
from alexa.api.views import JokeViewSet, action_stream
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'jokes', JokeViewSet)

urlpatterns = [
    path('', main_view),
    path('discussion', alexa_io),
    path('activity', include('actstream.urls')),
    path('act/', include(router.urls)),
    path('stream/', action_stream),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]
