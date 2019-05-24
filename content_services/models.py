import json
from datetime import datetime, timedelta

import requests
from django.db import models
from jsonfield import JSONField
from utilities.time import now_in_tz

from caressa.settings import OPEN_WEATHER_API_KEY
from senior_living_facility.models import SeniorLivingFacility
from utilities.models.abstract_models import CreatedTimeStampedModel
from utilities.logger import log
from utilities.speech import ssml_post_process
from utilities.template import template_to_str

WEATHER_TIME_DIFF_IN_SEC = 3600     # an hour


class InfoWeather(CreatedTimeStampedModel):
    class Meta:
        db_table = 'info_weather'

    API_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather?zip={zip_code},us&units=imperial&appid={api_id}"

    zip_code = models.CharField(max_length=5, null=False, blank=False, db_index=True, )
    is_call_successful = models.BooleanField(default=False)
    raw_data = JSONField(null=False, blank=False, )
    description = models.CharField(max_length=100, blank=True, )
    temperature_current = models.IntegerField()
    temperature_min = models.IntegerField()
    temperature_max = models.IntegerField()
    comment = models.TextField(blank=True, default='')

    @staticmethod
    def fetch_from_api(zip_code):
        log("Fetching weather info for {}".format(zip_code))

        url = InfoWeather.API_ENDPOINT.format(zip_code=zip_code, api_id=OPEN_WEATHER_API_KEY)
        return requests.get(url)

    @staticmethod
    def fetch_for(facility: SeniorLivingFacility = None, zip_code=None):
        assert any([facility, zip_code]), (
            "Either facility or zip_code is supposed to exist"
        )

        if facility and facility.zip_code:
            zip_code = facility.zip_code

        weather_qs = InfoWeather.objects.all().filter(
            created__gte=(now_in_tz('utc')-timedelta(seconds=WEATHER_TIME_DIFF_IN_SEC)),
            zip_code=zip_code,
            is_call_successful=True, )

        if weather_qs.count() > 0:
            return weather_qs[0]

        response = InfoWeather.fetch_from_api(zip_code)

        raw_data = json.loads(response.text)

        description = raw_data['weather'][0].get('description')
        temp_current = raw_data['main'].get('temp')
        temp_min = raw_data['main'].get('temp_min')
        temp_max = raw_data['main'].get('temp_max')
        comment = "It is a good day to be out" \
            if raw_data['weather'][0].get('main').lower() in ('clear', 'clouds', ) \
            else ""

        weather = InfoWeather.objects.create(zip_code=zip_code,
                                             is_call_successful=response.status_code == 200,
                                             raw_data=raw_data,
                                             description=description,
                                             temperature_current=temp_current,
                                             temperature_min=temp_min,
                                             temperature_max=temp_max,
                                             comment=comment, )

        return weather

    def get_text(self):
        assert self.is_call_successful, (
            "get_text() function can only be called for object with `is_call_successful=True`"
        )

        context = {
            'temperature_current': self.temperature_current,
            'temperature_max': self.temperature_max,
            'temperature_min': self.temperature_min,
            'description': self.description,
            'comment': self.comment,
        }

        template_with_context = template_to_str('speech/today-weather.ssml', context)
        return ssml_post_process(template_with_context)
