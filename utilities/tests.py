import pytz
import unittest

from unittest.mock import patch
from utilities.email import send_email
from utilities.speech import ssml_post_process
from utilities.sms import send_sms
from utilities.time import time_today_in_tz
from django.utils.timezone import localtime


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


class TestTime(unittest.TestCase):
    def test_time_today_in_tz(self):
        t_utc = time_today_in_tz('UTC', 15)
        current_utc = localtime(timezone=pytz.timezone('UTC'))
        self.assertEqual(t_utc.tzinfo.zone, 'UTC')
        self.assertEqual(t_utc.hour, 15)
        self.assertEqual(t_utc.minute, 0)
        self.assertEqual(t_utc.second, 0)
        self.assertEqual(t_utc.month, current_utc.month)
        self.assertEqual(t_utc.day, current_utc.day)

        t_la = time_today_in_tz('America/Los_Angeles', 1, 2, 3)
        current_la = localtime(timezone=pytz.timezone('America/Los_Angeles'))
        self.assertEqual(t_la.tzinfo.zone, 'America/Los_Angeles')
        self.assertEqual(t_la.hour, 1)
        self.assertEqual(t_la.minute, 2)
        self.assertEqual(t_la.second, 3)
        self.assertEqual(t_la.month, current_la.month)
        self.assertEqual(t_la.day, current_la.day)


class EmailTestCases(unittest.TestCase):
    @patch('utilities.email.EmailMultiAlternatives')
    def test_send_email(self, mock_email_multi_alternatives):
        def _attach_alternative(*args, **kwargs):
            return args, kwargs

        def _send():
            return True

        mock_email_multi_alternatives.return_value = _Response(attach_alternative=_attach_alternative,
                                                               send=_send)
        send_res, html_content, text_content, to_email_addresses = \
            send_email(['cuneyt@caressa.ai', 'info@caressa.ai'], 'Welcome Email', 'test/email.html',
                       'test/email.txt', context={'var1': 1, 'var2': 'Interesting'})
        self.assertTrue(send_res)
        self.assertEqual(html_content, "<div>Sample email content with <span>1</span> and Interesting</div>")
        self.assertEqual(text_content, "Sample email content with 1 and Interesting")
        self.assertListEqual(to_email_addresses, ['cuneyt@caressa.ai', 'info@caressa.ai'])
