from django.contrib.auth import views as auth_views
from django.urls import path
from senior_living_facility.views import facility_home, family_prospect_invitation, sign_up, app_downloads

from caressa.settings import WEB_CLIENT, API_URL

urls = [
    path('facility/', facility_home),
    path('login/',
         auth_views.LoginView.as_view(template_name='registration/login.html',
                                      extra_context={'api_base': API_URL,
                                                     'client_id': WEB_CLIENT['id'],
                                                     'client_secret': WEB_CLIENT['secret']}),
         name='login'),
    path('sign-up/', sign_up, name='sign-up'),
    path('app-downloads/', app_downloads, name='app-downloads'),
    path('invitation/', family_prospect_invitation, name='family-prospect-invitation-code'),
    path('password_reset/', auth_views.password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='password_reset_complete')
]