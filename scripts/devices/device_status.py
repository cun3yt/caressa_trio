import requests
import os
from utilities.logger import log
import json

email = os.environ.get('DATAPLICITY_USER')
password = os.environ.get('DATAPLICITY_PASSWD')
_api = 'https://apps.dataplicity.com/{path}'


def _get_token():
    url = _api.format(path='auth/')
    response = requests.post(url,
                             {'email': email, 'password': password})

    if response.status_code != 201:
        log('Failed with status code: {code}! Details: {details}'.format(details=response.text,
                                                                         code=response.status_code, ))
        exit(1)

    res_body = json.loads(response.text)
    return res_body.get('token')


def _get_headers(token):
    return {'Authorization': 'Token {}'.format(token)}


def _get_devices(token):
    url = _api.format(path='devices/')
    response = requests.get(url, headers=_get_headers(token))
    return json.loads(response.text)


def run():
    """
    Sample usage: `./manage.py runscript devices.device_status --script-args <smt>`
    """
    token = _get_token()
    devices = _get_devices(token)
    print(devices)
