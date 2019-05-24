from alexa.models import User
from typing import Union

from content_services.models import InfoWeather
from senior_living_facility.models import SeniorLivingFacilityContent, ContentDeliveryRule
from utilities.logger import log, log_error
from utilities.speech import ssml_post_process
from utilities.template import template_to_str
from utilities.time import time_today_in_tz

errors = {
    'wrong_script_usage': {
        'msg': "Wrong script usage. "
               "`./manage.py runscript scripts.senior_living_facility.content_delivery.personalized_morning_content "
               "--script-args <function_name> <args_to_function>`\n"
               "    Examples:\n"
               "    `./manage.py runscript scripts.senior_living_facility.content_delivery.personalized_morning_content"
               " --script-args send_for_individual 1`\n",
        'code': 1,
    },
}


def _get_user(user: Union[User, int, str]) -> User:
    if isinstance(user, str):
        user = int(user)
    if isinstance(user, int):
        user = User.objects.get(id=user)
    return user


def _send_realtime_message(user, content):
    raise NotImplementedError


def _get_todays_date_text(user: User):
    now = user.senior_living_facility.get_now_in_tz()
    context = {
        "weekday": now.strftime("%A"),
        'month': now.month,
        'day': now.day,
    }
    template_with_context = template_to_str('speech/todays-date.ssml', context)
    return ssml_post_process(template_with_context)


def send_for_individual(user: Union[User, int, str]):
    user = _get_user(user)

    # todo do the content generation

    content = "something here..."

    date_text = _get_todays_date_text(user)

    facility = user.senior_living_facility

    info_weather = InfoWeather.fetch_for(facility)

    weather_text = info_weather.get_text()

    context = {
        'name': user.first_name,
        'todays_date': date_text,
        'weather': weather_text,
    }

    template_with_context = template_to_str('speech/resident-good-morning.ssml', context)
    output = ssml_post_process(template_with_context)

    content = SeniorLivingFacilityContent.find(delivery_type=ContentDeliveryRule.TYPE_INJECTABLE,
                                               start=time_today_in_tz(facility.timezone, 5, 0),
                                               end=time_today_in_tz(facility.timezone, 11, 59),
                                               frequency=0,
                                               recipient_ids=None,
                                               senior_living_facility=facility,
                                               content_type=SeniorLivingFacilityContent.TYPE_DAILY_CALENDAR,
                                               ssml_content=output)

    # _send_realtime_message(user, content)


def run(fn_name=None, *args):
    """
    Usage: See `errors` dictionary above for the script usage usage.
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
