from utilities.logger import log, log_debug, log_error
from senior_living_facility.models import SeniorLivingFacility, SeniorDevice, SeniorLivingFacilityContent, \
    SeniorLivingFacilityMessageLog as MsgLog
from caressa.settings import pusher_client
from alexa.models import User
from datetime import datetime, timedelta
from typing import Union
import pytz


errors = {
    'wrong_script_usage': {
        'msg': "Wrong script usage. "
               "`./manage.py runscript scripts.morning_check_in --script-args <function_name> <args_to_function>`\n"
               "    Examples:\n"
               "        `./manage.py runscript scripts.morning_check_in --script-args "
               "send_check_in_call_for_one_facility 123`\n"
               "        `./manage.py runscript scripts.morning_check_in --script-args "
               "send_check_in_call_for_all_facilities`\n",
        'code': 1,
    },
}


def _can_send_for_facility(facility: SeniorLivingFacility) -> 'bool':
    # Two checks here:
    #   1. Has time come for remind to check in?
    #   2. Did we send it today before this attempt?
    if not facility.check_in_reminder:
        log("Check in reminder time is not set for facility: ({}, {}). Passing it".format(facility.id, facility.name))
        return False

    if not facility.has_check_in_reminder_passed():
        log("Check in reminder time is not come for facility: ({}, {}). Passing it".format(facility.id, facility.name))
        return False

    now = datetime.now(pytz.utc)
    reminder_limit_after_deadline_in_minutes = 45
    if now - timedelta(minutes=reminder_limit_after_deadline_in_minutes) > facility.deadline_in_time_today_in_tz:
        log("Check in reminder is not available after {} minutes from deadline. Passing it".format(reminder_limit_after_deadline_in_minutes))
        return False

    message_log_qs = MsgLog.objects.filter(senior_living_facility=facility,
                                           content_type=MsgLog.CONTENT_TYPE_CALL_FOR_MORNING_CHECK_IN).order_by(
        '-created')

    if message_log_qs.count() > 0:
        message_log = message_log_qs[0]
        interval_in_hours = 12
        if (now - timedelta(hours=interval_in_hours)) < message_log.created:
            log("Check in reminded in the last {} hours for facility ({}, {}). Passing it".format(interval_in_hours,
                                                                                                  facility.id,
                                                                                                  facility.name))
            return False

    return True


def send_check_in_call_for_one_facility(facility: Union[SeniorLivingFacility, int]):
    if isinstance(facility, int):
        facility = SeniorLivingFacility.objects.get(id=facility)

    if not _can_send_for_facility(facility):
        return

    recipient_ids = facility.get_resident_ids_with_device_but_not_checked_in()

    channel = User.get_facility_channel(facility.facility_id)

    text = SeniorDevice.call_for_action_text()

    content = SeniorLivingFacilityContent.find(senior_living_facility=facility,
                                               content_type='Check-In-Call',
                                               text_content=text)

    log("Running Check In Call to Action: `send_check_in_call` with: ")
    log("  recipient user ids (not check in seniors' user IDs): {}".format(', '.join(map(str, recipient_ids))))
    log("  on channel: {}".format(channel))
    log("  text: {}".format(text))
    log("  SeniorLivingFacilityContent.hash: {}".format(content.text_content_hash))

    MsgLog.objects.create(senior_living_facility=facility,
                          content_type=MsgLog.CONTENT_TYPE_CALL_FOR_MORNING_CHECK_IN,
                          medium_type=MsgLog.MEDIUM_TYPE_TEXT,
                          delivery_type=MsgLog.DELIVERY_TYPE_URGENT_MAIL,
                          data={'recipient_ids': recipient_ids})

    pusher_client.trigger(channel,
                          'urgent_mail',
                          {
                              'url': content.audio_url,
                              'is_selected_recipient_type': True,
                              'selected_recipient_ids': recipient_ids
                          })


def send_check_in_call_for_all_facilities():
    facilities = SeniorLivingFacility.objects.all()

    for facility in facilities:
        log("Running for Facility: {}".format(facility.facility_id))
        send_check_in_call_for_one_facility(facility)


def run(fn_name=None, *args):
    """
    Usage: `./manage.py runscript scripts.morning_check_in --script-args <function_name> <args_to_function>`
        Examples:
            `./manage.py runscript scripts.morning_check_in --script-args send_check_in_call_for_one_facility 123`
            `./manage.py runscript scripts.morning_check_in --script-args send_check_in_call_for_all_facilities`
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
