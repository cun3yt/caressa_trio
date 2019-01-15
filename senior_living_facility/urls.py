from django.urls import path
from senior_living_facility.views import facility_home


urls = [
    path('', facility_home),
]
