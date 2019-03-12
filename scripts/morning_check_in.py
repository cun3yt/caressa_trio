from utilities.logger import log, log_debug, log_error
from senior_living_facility.models import SeniorLivingFacility, SeniorDevice, SeniorLivingFacilityContent
from caressa.settings import pusher_client
from alexa.models import User


errors = {
    'wrong_script_usage': {
        'msg': "Wrong script usage. "
               "`./manage.py runscript scripts.morning_check_in --script-args <function_name> <args_to_function>`",
        'code': 1,
    },
}


def send_check_in_call(senior_living_facility_id):
    facility = SeniorLivingFacility.objects.get(id=senior_living_facility_id)
    recipient_ids = facility.get_resident_ids_with_device_but_not_checked_in()

    log_debug(recipient_ids)
    log_debug("recipients: {}".format(', '.join( map(str, recipient_ids))))

    channel = User.get_facility_channel(facility.facility_id)

    text = SeniorDevice.call_for_action_text()

    content = SeniorLivingFacilityContent.find(senior_living_facility=facility,
                                               content_type='Check-In-Call',
                                               text_content=text)

    log(content.audio_url)
    log(channel)
    log(recipient_ids)

    pusher_client.trigger(channel,
                          'urgent_mail',
                          {
                              'url': content.audio_url,
                              'is_selected_recipient_type': True,
                              'selected_recipient_ids': recipient_ids
                          })


def run(fn_name=None, *args):
    """
    Usage: `./manage.py runscript scripts.morning_check_in --script-args <function_name> <args_to_function>`
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
