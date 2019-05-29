from django.utils.crypto import get_random_string

from alexa.models import User
from typing import Union

from content_services.models import InfoWeather
from senior_living_facility.models import SeniorLivingFacilityContent, ContentDeliveryRule
from utilities.aws_operations import upload_mp3_to_s3
from utilities.file_operations import concat_mp3_files
from utilities.logger import log, log_error
from utilities.real_time_communication import send_instance_message
from utilities.speech import ssml_post_process
from utilities.template import template_to_str
from utilities.time import time_today_in_tz
from voice_service.google.tts import tts

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


def _send_realtime_message(user: User, content: SeniorLivingFacilityContent):
    """
    Send the `content` to all residents of the `facility` as a real-time message
    :param facility:
    :param content:
    :return:
    """

    rule = content.delivery_rule
    channel = User.get_facility_channel(user.senior_living_facility.facility_id)
    send_instance_message(channel,
                          'injectable_content',
                          {
                              'url': content.audio_url,
                              'hash': content.hash,
                              'start': rule.start.timestamp(),
                              'end': rule.end.timestamp(),
                          })


def _get_todays_date_text(user: User):
    now = user.senior_living_facility.get_now_in_tz()
    context = {
        "weekday": now.strftime("%A"),
        'month': now.month,
        'day': now.day,
    }
    template_with_context = template_to_str('speech/todays-date.ssml', context)
    return ssml_post_process(template_with_context)


def _prepare_filler_content():
    default_context = {
        'after_break_ms': 1400,
    }
    text_contents = [
        {
            'ssml': 'speech/morning/filler-news.ssml',
            'gender': 'female'
        },
        {
            'ssml': 'speech/morning/filler-medicine-delivery.ssml',
            'gender': 'male'
        },
        {
            'ssml': 'speech/morning/filler-activity.ssml',
            'gender': 'female'
        },
        {
            'ssml': 'speech/morning/filler-joke-feedback.ssml',
            'gender': 'male'
        },
        {
            'ssml': 'speech/morning/filler-maybe-like.ssml',
            'gender': 'female'
        },
    ]

    output_files = []

    for content in text_contents:
        template_with_context = template_to_str(content['ssml'], default_context)
        ssml = ssml_post_process(template_with_context)
        _, filepath = tts(ssml=ssml, gender=content.get('gender', 'male'))
        output_files.append(filepath)

    concat_filename = 'concat_{}.mp3'.format(get_random_string(25))
    output_local_mp3 = concat_mp3_files(output_files, concat_filename)
    url = upload_mp3_to_s3('filler-content/{}'.format(concat_filename),
                           output_local_mp3,
                           return_format='url')
    return url


def send_for_individual(user: Union[User, int, str]):
    user = _get_user(user)

    date_text = _get_todays_date_text(user)

    facility = user.senior_living_facility

    info_weather = InfoWeather.fetch_for(facility)

    weather_text = info_weather.get_text()

    filler_content_url = _prepare_filler_content()

    context = {
        'name': user.first_name,
        'todays_date': date_text,
        'weather': weather_text,
        'filler_content_url': filler_content_url,
    }

    template_with_context = template_to_str('speech/resident-good-morning.ssml', context)
    output = ssml_post_process(template_with_context)

    content = SeniorLivingFacilityContent.find(delivery_type=ContentDeliveryRule.TYPE_INJECTABLE,
                                               start=time_today_in_tz(facility.timezone, 5, 0),
                                               end=time_today_in_tz(facility.timezone, 11, 59),
                                               frequency=0,
                                               recipient_ids=None,
                                               senior_living_facility=facility,
                                               content_type=SeniorLivingFacilityContent.TYPE_MORNING_FIRST_CONTENT,
                                               ssml_content=output)

    # todo 1. Should `SeniorLivingFacilityContent` have its own method to deliver according to the `delivery_rule`?
    # todo 2. Delivery and Delivery analytics require a design

    _send_realtime_message(user, content)


def run(fn_name=None, *args):
    """
    Usage: See `errors` dictionary above for the script usage.
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
