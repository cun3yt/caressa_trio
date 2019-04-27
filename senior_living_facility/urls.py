from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from senior_living_facility.views import facility_home, facility_settings, family_prospect_invitation, sign_up, \
    app_downloads
from senior_living_facility.api.views import SeniorLivingFacilityViewSet, SeniorDeviceUserActivityLogCreateViewSet, \
    FacilityViewSet, FacilityListViewSet, SeniorLivingFacilityContentViewSet, \
    MessageThreadMessagesViewSet, ServiceRequestViewSet, uploaded_new_profile_picture, FacilityMessageViewSet, \
    PhotoGalleryViewSet, PhotosDayViewSet, FacilityResidentTodayCheckInViewSet, MessagesThreadParticipantViewSet, \
    MessageThreadViewSet, CalendarViewSet
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
    path('api/facility/<int:pk>/message/',
         FacilityMessageViewSet.as_view({'post': 'create', })),
    path('api/facility/<int:pk>/messages/',
         MessagesThreadParticipantViewSet.as_view({'get': 'list', })),
    path('api/residents/<int:pk>/checked/today/',
         FacilityResidentTodayCheckInViewSet.as_view({'post': 'create', 'delete': 'destroy', }),
         name='morning-check-in'),
    path('api/message-thread/<int:pk>/',
         MessageThreadViewSet.as_view({'get': 'retrieve'}), name='message-thread',),
    path('api/message-thread/<int:pk>/messages/',
         MessageThreadMessagesViewSet.as_view({'get': 'list', }), name='message-thread-messages'),
    path('api/users/me/contents/',
         SeniorLivingFacilityContentViewSet.as_view({'get': 'list'})),
    path('api/users/<int:id>/uploaded_new_profile_picture/',
         uploaded_new_profile_picture, name='uploaded_new_profile_picture',),
    path('api/users/me/service-requests/',
         ServiceRequestViewSet.as_view({'post': 'create'})),
    path('api/photo-galleries/<int:pk>/',
         PhotoGalleryViewSet.as_view({'get': 'list', }), name='photo-gallery'),
    path('api/photo-galleries/<int:pk>/days/<slug:date>/',
         PhotosDayViewSet.as_view({'get': 'list', }), name='photo-day-view'),
    path('api/calendars/<int:pk>/',
         CalendarViewSet.as_view(), name='calendar'),
]
