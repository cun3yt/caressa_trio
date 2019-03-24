from utilities.logger import log, log_error
from senior_living_facility.models import SeniorLivingFacility, SeniorLivingFacilityContent
from alexa.models import User
from typing import Union
from caressa.settings import pusher_client
from utilities.time import time_today_in_tz


errors = {
    'wrong_script_usage': {
        'msg': "Wrong script usage. "
               "`./manage.py runscript scripts.senior_living_facility.content_delivery.calendar "
               "--script-args <function_name> <args_to_function>`\n"
               "    Examples:\n"
               "        `./manage.py runscript scripts.senior_living_facility.content_delivery.calendar "
               "--script-args deliver_daily_calendar 1`\n",
        'code': 1,
    },
}


def deliver_daily_calendar(facility: Union[SeniorLivingFacility, int, str]):
    if isinstance(facility, str):
        facility = int(facility)

    if isinstance(facility, int):
        facility = SeniorLivingFacility.objects.get(id=facility)

    events_summary = facility.today_events_summary_in_text()

    from senior_living_facility.models import ContentDeliveryRule

    content = SeniorLivingFacilityContent.find(delivery_type=ContentDeliveryRule.TYPE_INJECTABLE,
                                               start=time_today_in_tz(facility.timezone, 1, 0),
                                               end=time_today_in_tz(facility.timezone, 16, 0),
                                               frequency=0,
                                               recipient_ids=None,
                                               senior_living_facility=facility,
                                               content_type=SeniorLivingFacilityContent.TYPE_DAILY_CALENDAR,
                                               text_content=events_summary)

    rule = content.delivery_rule

    # todo Save to an API-oriented serve-able location for querying content existence

    channel = User.get_facility_channel(facility.facility_id)

    pusher_client.trigger(channel,
                          'injectable_content',
                          {
                              'url': content.audio_url,
                              'hash': content.text_content_hash,    # to avoid repetition
                              'start': rule.start.timestamp(),
                              'end': rule.end.timestamp(),
                          })


def run(fn_name=None, *args):
    """
    Usage: `./manage.py runscript scripts.senior_living_facility.content_delivery.calendar --script-args <function_name> <args_to_function>`
        Examples:
            `./manage.py runscript scripts.senior_living_facility.content_delivery.calendar --script-args deliver_daily_calendar 1`
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
