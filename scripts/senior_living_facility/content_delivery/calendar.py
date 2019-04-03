from utilities.logger import log, log_error
from senior_living_facility.models import SeniorLivingFacility, SeniorLivingFacilityContent, ContentDeliveryRule
from alexa.models import User
from typing import Union
from caressa.settings import pusher_client
from utilities.time import time_today_in_tz
from datetime import timedelta


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


def _get_facility(facility: Union[SeniorLivingFacility, int, str]) -> SeniorLivingFacility:
    if isinstance(facility, str):
        facility = int(facility)
    if isinstance(facility, int):
        facility = SeniorLivingFacility.objects.get(id=facility)
    return facility


def _send_realtime_message(facility: SeniorLivingFacility, content: SeniorLivingFacilityContent):
    """
    Send the `content` to all residents of the `facility` as a real-time message
    :param facility:
    :param content:
    :return:
    """

    rule = content.delivery_rule
    channel = User.get_facility_channel(facility.facility_id)
    pusher_client.trigger(channel,
                          'injectable_content',
                          {
                              'url': content.audio_url,
                              'hash': content.hash,
                              'start': rule.start.timestamp(),
                              'end': rule.end.timestamp(),
                          })


def deliver_daily_calendar(facility: Union[SeniorLivingFacility, int, str]):
    facility = _get_facility(facility)

    events_summary = facility.today_events_summary_in_text()
    content = SeniorLivingFacilityContent.find(delivery_type=ContentDeliveryRule.TYPE_INJECTABLE,
                                               start=time_today_in_tz(facility.timezone, 1, 0),
                                               end=time_today_in_tz(facility.timezone, 16, 0),
                                               frequency=0,
                                               recipient_ids=None,
                                               senior_living_facility=facility,
                                               content_type=SeniorLivingFacilityContent.TYPE_DAILY_CALENDAR,
                                               text_content=events_summary)

    _send_realtime_message(facility, content)


def deliver_upcoming_hourly_events(facility: Union[SeniorLivingFacility, int, str]):
    facility = _get_facility(facility)

    events = facility.get_today_events()
    hourly_events = events.get('hourly_events')

    for event in hourly_events.get('set'):
        try:
            text_content = facility.get_text_for_hourly_event(event, 30)
        except AssertionError as err:
            print("There is an Assertion Error for `get_text_for_hourly_event`: {0}".format(err))
        else:
            announcement_time = {
                'start': event['start'] - timedelta(minutes=45),
                'end': event['start'] - timedelta(minutes=15),
            }

            content = SeniorLivingFacilityContent.find(delivery_type=ContentDeliveryRule.TYPE_INJECTABLE,
                                                       start=announcement_time['start'],
                                                       end=announcement_time['end'],
                                                       frequency=0,
                                                       recipient_ids=None,
                                                       senior_living_facility=facility,
                                                       content_type=SeniorLivingFacilityContent.TYPE_UPCOMING_INDIVIDUAL_EVENT,
                                                       text_content=text_content)
            _send_realtime_message(facility, content)


def run(fn_name=None, *args):
    """
    Usage: `./manage.py runscript scripts.senior_living_facility.content_delivery.calendar --script-args <function_name> <args_to_function>`
        Examples:
            `./manage.py runscript scripts.senior_living_facility.content_delivery.calendar --script-args deliver_daily_calendar 1`
            `./manage.py runscript scripts.senior_living_facility.content_delivery.calendar --script-args deliver_upcoming_hourly_events 1`
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
