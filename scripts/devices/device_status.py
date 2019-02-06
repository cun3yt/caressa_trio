import requests
import os
from utilities.logger import log
import json
import pprint
from senior_living_facility.models import SeniorDevice, SeniorDevicesRawLog


errors = {
    'token_fetch': {
        'msg': "Token Retrieval failed with status code: {code}! Details: {details}",
        'code': 1,
    },
    'device_fetch': {
        'msg': "Fetching devices failed with status code: {code}. Details: {details}",
        'code': 2,
    },
    'token_invalidation': {
        'msg': "Token invalidation failed with status code: {code}. Expected code was {expected}",
        'code': None,
    },
    'wrong_script_usage': {
        'msg': "Wrong script usage. "
               "`./manage.py runscript devices.device_status --script-args <function_name> <args_to_function>`",
        'code': 3,
    },
}

_email = os.environ.get('DATAPLICITY_USER')
_password = os.environ.get('DATAPLICITY_PASSWD')
_api = 'https://apps.dataplicity.com/{path}'


def _get_token():
    expected_code = 201
    url = _api.format(path='auth/')
    response = requests.post(url, {'email': _email, 'password': _password})

    if response.status_code != expected_code:
        error = errors['token_fetch']
        log(error['msg'].format(details=response.text, code=response.status_code))
        exit(error['code'])

    res_body = json.loads(response.text)
    return res_body.get('token')


def _get_headers(token):
    return {'Authorization': 'Token {}'.format(token)}


def _get_devices(token):
    expected_code = 200
    url = _api.format(path='devices/')
    response = requests.get(url, headers=_get_headers(token))

    if response.status_code != expected_code:
        error = errors['device_fetch']
        log(error['msg'].format(code=response.status_code, details=response.text))
        exit(error['code'])

    return json.loads(response.text)


def _invalidate_token(token):
    expected_code = 204

    url = _api.format(path='auth/')
    response = requests.delete(url, headers=_get_headers(token))

    if response.status_code != expected_code:
        error = errors['token_invalidation']
        log(error['msg'].format(code=response.status_code, expected=expected_code))
        # Invalidation error is not critical, there is no blocker for further processing (no exit)


def fetch_raw_log(dry_run=False):
    dry_run = dry_run == 'True' if isinstance(dry_run, str) else dry_run

    token = _get_token()
    devices = _get_devices(token)
    _invalidate_token(token)

    log('Dry Run: {}'.format('YES' if dry_run else 'NO'))
    num_devices = len(devices)
    log("Number of Devices: {}".format(num_devices))

    if dry_run:
        log("Each device details: ")
        ppr = pprint.PrettyPrinter()
        formatter = ppr.pformat
        for _ind, device in enumerate(devices, start=1):
            log("** Detail ({}. {}) **".format(_ind, device.get('serial')))
            log(formatter(device))
            log("--------")
        return None

    raw_log = SeniorDevicesRawLog.objects.create(data=devices)
    log('SeniorDevicesRawLog is saved')
    return raw_log


def create_device_statuses(raw_log: SeniorDevicesRawLog = None):
    if not raw_log:
        log("Raw log is not provided, fetching the latest one")
        raw_log = SeniorDevicesRawLog.objects.order_by('-pk').all()[0]

    log("Saving individual SeniorDevice (online/offline) state "
        "by processing SeniorDevicesRawLog::{pk}".format(pk=raw_log.id))

    devices = raw_log.data
    num_devices = len(devices)

    for _ind, device in enumerate(devices, start=1):
        log('Processing {} of {}'.format(_ind, num_devices))
        serial = device.get('serial')
        is_online = device.get('online')
        SeniorDevice.objects.update_or_create(serial=serial,
                                              defaults={
                                                  'is_online': is_online,
                                                  'raw_log': raw_log,
                                                  'status_checked': raw_log.modified,
                                              })
    log('Device statuses are saved successfully.')


def fetch_and_process_device_statuses():
    raw_log = fetch_raw_log()
    create_device_statuses(raw_log)


def run(fn_name=None, *args):
    """
    Usage: `./manage.py runscript scripts.devices.device_status --script-args <function_name> <args_to_function>`
    To fetch raw log:
        * (Dry Run) `./manage.py runscript scripts.devices.device_status --script-args fetch_raw_log True`
        * `./manage.py runscript scripts.devices.device_status --script-args fetch_raw_log False`
    To create device statuses from the latest raw log (this log must have been created before):
        * `./manage.py runscript scripts.devices.device_status --script-args create_device_statuses`
    To run both fetching raw log and saving to the statuses to the database:
        * `./manage.py runscript scripts.devices.device_status --script-args fetch_and_process_device_statuses`
    """

    if fn_name is None:
        error = errors['wrong_script_usage']
        log(error['msg'])
        exit(error['code'])

    log('Running {}'.format(fn_name))
    globals()[fn_name](*args)
