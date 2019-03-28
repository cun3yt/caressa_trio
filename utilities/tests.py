import unittest
from unittest.mock import patch
from utilities.speech import ssml_post_process
from utilities.sms import send_sms


class _Response:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class TestSsmlPlayer(unittest.TestCase):
    def test_ssml_post_process(self):
        ssml = "   Hello XYZ,   this is    a beautiful  day outside.    Don 't you  think     so  ? "
        expected_ssml = "Hello XYZ, this is a beautiful day outside. Don 't you think so ?"
        self.assertEqual(expected_ssml, ssml_post_process(ssml))


class TestSms(unittest.TestCase):
    @patch('utilities.sms.Client')
    def test_send_sms(self, mock_twilio_client):
        def _create(*args, **kwargs):
            return _Response(date_sent='some-date-info',
                             direction='some-direction',
                             body='some-body',
                             from_='some-from')
        mock_twilio_client.return_value = _Response(messages=_Response(create=_create))
        res, text_content, phone_no = send_sms('+1 415-533-7523',
                                               {'var1': 'hey', 'var2': 222},
                                               'test/sms.txt')
        self.assertEqual(res, {'date_sent': 'some-date-info',
                               'direction': 'some-direction',
                               'body': 'some-body',
                               'from': 'some-from'})
        self.assertEqual(text_content, "Hello this is an sms with variable 1: hey and variable 2: 222")
        self.assertEqual(phone_no, '+1 415-533-7523')
