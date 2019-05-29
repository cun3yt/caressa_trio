from datetime import timedelta
from typing import Union

from alexa.models import User
from senior_living_facility.models import SeniorLivingFacility, SeniorLivingFacilityContent, ContentDeliveryRule
from utilities.logger import log_error, log
from utilities.real_time_communication import send_instance_message

errors = {
    'wrong_script_usage': {
        'msg': "Wrong script usage. "
               "`./manage.py runscript scripts.senior_living_facility.content_delivery.meal "
               "--script-args <function_name> <args_to_function>`\n"
               "    Examples:\n"
               "        `./manage.py runscript scripts.senior_living_facility.content_delivery.meal "
               "--script-args generate_daily_meal_content 1`\n",
        'code': 1,
    },
}


def _get_facility(facility: Union[SeniorLivingFacility, int, str]) -> SeniorLivingFacility:
    if isinstance(facility, str):
        facility = int(facility)
    if isinstance(facility, int):
        facility = SeniorLivingFacility.objects.get(id=facility)
    return facility


def generate_daily_meal_content(facility: Union[SeniorLivingFacility, int, str]):
    facility = _get_facility(facility)

    meals = facility.get_today_meal_plan()
    meal_set = meals.get('set')

    for meal in meal_set:
        try:
            ssml_content = facility.get_ssml_for_meal(meal)
        except AssertionError as err:
            print("here is an Assertion Error for `get_ssml_for_meal`: {0}".format(err))
        else:
            announcement_time = {
                'start': meal['start'],
                'end': meal['end'] - timedelta(minutes=15),
            }

            SeniorLivingFacilityContent.find(delivery_type=ContentDeliveryRule.TYPE_INJECTABLE,
                                             start=announcement_time['start'],
                                             end=announcement_time['end'],
                                             frequency=1,
                                             recipient_ids=None,
                                             senior_living_facility=facility,
                                             content_type=SeniorLivingFacilityContent.TYPE_MEAL_ANNOUNCEMENT,
                                             ssml_content=ssml_content, )


def run(fn_name=None, *args):
    """
    Usage: `./manage.py runscript scripts.senior_living_facility.content_delivery.meal --script-args <function_name> <args_to_function>`
        Examples:
            `./manage.py runscript scripts.senior_living_facility.content_delivery.meal --script-args generate_daily_meal_content 1`
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log_error(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
