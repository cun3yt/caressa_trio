from django.contrib.auth import views as auth_views
from django.urls import path
from senior_living_facility.views import facility_home

from caressa.settings import WEB_CLIENT, API_URL

urls = [
    path('facility/', facility_home),
    path('login/',
         auth_views.LoginView.as_view(template_name='registration/login.html',
                                      extra_context={'api_base': API_URL,
                                                     'client_id': WEB_CLIENT['id'],
                                                     'client_secret': WEB_CLIENT['secret']}),
         name='login'),
]
