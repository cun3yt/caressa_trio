from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from senior_living_facility.mock.views import message_thread
from senior_living_facility.views import facility_home, facility_settings, family_prospect_invitation, sign_up, \
    app_downloads
from senior_living_facility.api.views import SeniorLivingFacilityViewSet, SeniorDeviceUserActivityLogCreateViewSet, \
    FacilityViewSet, FacilityListViewSet, SeniorLivingFacilityContentViewSet, FacilityMessagesViewSet,\
    MessageThreadMessagesViewSet
from caressa.settings import WEB_CLIENT, API_URL

urls = [
    path('facility/', facility_home),
    path('settings/', facility_settings),
    path('login/',
         auth_views.LoginView.as_view(template_name='registration/login-js.html',
                                      extra_context={'api_base': API_URL,
                                                     'client_id': WEB_CLIENT['id'],
                                                     'client_secret': WEB_CLIENT['secret'],
                                                     'forget_password_url': reverse_lazy('password_reset')}),
         name='login'),
    path('sign-up/', sign_up, name='sign-up'),
    path('app-downloads/', app_downloads, name='app-downloads'),
    path('invitation/', family_prospect_invitation, name='family-prospect-invitation-code'),
    path('password_reset/', auth_views.password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
]

api_urls = [
    path('api/senior_living_facilities/<int:pk>/',
         SeniorLivingFacilityViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', })),
    path('api/user-activity-log/',
         SeniorDeviceUserActivityLogCreateViewSet.as_view({'post': 'create'})),
    path('api/facility/<int:pk>/',
         FacilityViewSet.as_view({'get': 'retrieve', })),
    path('api/facility/<int:senior_living_facility_id>/residents/',
         FacilityListViewSet.as_view({'get': 'list', })),
    path('api/facility/<int:pk>/messages/',
         FacilityMessagesViewSet.as_view({'get': 'list', })),
    path('api/message-threads/<int:pk>/', message_thread, name='mock_message_thread',),
    path('api/message-threads/<int:pk>/messages/',
         MessageThreadMessagesViewSet.as_view({'get': 'list', })),
    path('api/users/me/contents/',
         SeniorLivingFacilityContentViewSet.as_view({'get': 'list'})),
]
