import pytz
import unittest

from unittest.mock import patch

from caressa.settings import API_URL
from utilities.api.urls import reverse
from utilities.email import send_email
from utilities.speech import ssml_post_process
from utilities.sms import send_sms
from utilities.time import time_today_in_tz
from django.utils.timezone import localtime
from utilities.dictionaries import deep_get, deep_set


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


class TestDeepGet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dict_empty = {}
        cls.dict_1x5 = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
        }
        cls.dict_2x3 = {
            'level_1_a': {
                'level_2_a': 'aa',
                'level_2_b': 'ab',
                'level_2_c': 'ac',
            },
            'level_1_b': {
                'level_2_a': 'ba',
                'level_2_b': 'bb',
                'level_2_c': 'bc',
            },
        }
        cls.dict_deep = {
            'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': 'very_deep'}}}}}}}
        }
        cls.dict_case_sensitive = {
            'abc': {
                'DeF': 'hapat',
                'def': 'zapata',
            },
            'aBC': 2,
            'AbC': 3,
        }

    def test_deep_default_value(self):
        self.assertIsNone(deep_get(self.dict_empty, 'question_mark'))
        self.assertEqual(deep_get(self.dict_empty, 'question_mark', 'n/a'), 'n/a')

        self.assertIsNone(deep_get(self.dict_empty, 'a.b.c.d'))
        self.assertEqual(deep_get(self.dict_empty, 'a.b.c.d', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_1x5, 'a.b.c.d'))
        self.assertEqual(deep_get(self.dict_1x5, 'a.b.c.d', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_1x5, 'z'))
        self.assertEqual(deep_get(self.dict_1x5, 'z', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'level_1_a.xyz'))
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.xyz', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'xyz.level_2_a'))
        self.assertEqual(deep_get(self.dict_2x3, 'xyz.level_2_a', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'level_1_a.level_2_a.level3'))
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.level_2_a.level3', 1234), 1234)

        self.assertIsNone(deep_get(self.dict_2x3, 'level_1_X'))
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_X', 1234), 1234)

    def test_level_1(self):
        self.assertEqual(deep_get(self.dict_1x5, 'a'), 1)
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a'), {
            'level_2_a': 'aa',
            'level_2_b': 'ab',
            'level_2_c': 'ac',
        })

    def test_level_2(self):
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.level_2_a'), 'aa')
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_a.level_2_b'), 'ab')
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_b.level_2_c'), 'bc')
        self.assertEqual(deep_get(self.dict_2x3, 'level_1_b.level_2_a'), 'ba')

    def test_very_deep(self):
        self.assertEqual(deep_get(self.dict_deep, 'a.b.c.d.e.f.g.h'), 'very_deep')
        self.assertEqual(deep_get(self.dict_deep, 'a.b.c.d.e.f.g'), {'h': 'very_deep'})
        self.assertIsNone(deep_get(self.dict_deep, 'a.b.c.d.e.f.g.h.i.j.k'))
        self.assertIsNone(deep_get(self.dict_deep, 'a.b.c.d.e.f.g.h.i'))
        self.assertIsNone(deep_get(self.dict_deep, 'a.b.c.d.e.f.XX'))

    def test_case_sensitive(self):
        self.assertIsNone(deep_get(self.dict_case_sensitive, 'ABC'))
        self.assertIsNone(deep_get(self.dict_case_sensitive, 'abc.dEF'))
        self.assertEqual(deep_get(self.dict_case_sensitive, 'abc.DeF'), 'hapat')
        self.assertEqual(deep_get(self.dict_case_sensitive, 'AbC'), 3)
        self.assertEqual(deep_get(self.dict_case_sensitive, 'abc'), {
            'DeF': 'hapat',
            'def': 'zapata',
        })


class TestDeepSet(unittest.TestCase):
    def setUp(self):
        self.dict_empty = {}
        self.dict_1x5 = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
        }
        self.dict_2x3 = {
            'level_1_a': {
                'level_2_a': 'aa',
                'level_2_b': 'ab',
                'level_2_c': 'ac',
            },
            'level_1_b': {
                'level_2_a': 'ba',
                'level_2_b': 'bb',
                'level_2_c': 'bc',
            },
        }
        self.dict_deep = {
            'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': 'very_deep'}}}}}}}
        }
        self.dict_case_sensitive = {
            'abc': {
                'DeF': 'hapat',
                'def': 'zapata',
            },
            'aBC': 2,
            'AbC': 3,
        }

    def test_set_level_1_update(self):
        deep_set(self.dict_1x5, 'a', 12345)
        self.assertDictEqual(self.dict_1x5, {'a': 12345, 'b': 2, 'c': 3,
                                             'd': 4, 'e': 5, })

    def test_set_level_1_new_entry(self):
        deep_set(self.dict_1x5, 'f', 12345)
        self.assertDictEqual(self.dict_1x5, {'a': 1, 'b': 2, 'c': 3,
                                             'd': 4, 'e': 5, 'f': 12345})

    def test_set_level_1_update_deep(self):
        deep_set(self.dict_1x5, 'a.level2.level3', 12345)
        self.assertDictEqual(self.dict_1x5, {'a': {'level2': {'level3': 12345}}, 'b': 2, 'c': 3,
                                             'd': 4, 'e': 5})

    def test_set_level_1_new_deep(self):
        deep_set(self.dict_1x5, 'new_entry.level2.level3', 12345)
        self.assertDictEqual(self.dict_1x5, {'a': 1, 'b': 2, 'c': 3,
                                             'd': 4, 'e': 5, 'new_entry': {'level2': {'level3': 12345}}})

    def test_set_level_2_update(self):
        deep_set(self.dict_2x3, 'level_1_a.level_2_a', 'ffff')
        self.assertEqual(self.dict_2x3['level_1_a']['level_2_a'], 'ffff')

    def test_set_level_2_new_entry(self):
        deep_set(self.dict_2x3, 'level_1_a.level_2_f', {'x': 1})
        self.assertDictEqual(self.dict_2x3['level_1_a']['level_2_f'], {'x': 1})

    def test_set_case_sensitive(self):
        deep_set(self.dict_case_sensitive, 'aBC', 123)
        deep_set(self.dict_case_sensitive, 'abc.DEF', {'a': 12})
        self.assertDictEqual(self.dict_case_sensitive, {
            'abc': {
                'DeF': 'hapat',
                'def': 'zapata',
                'DEF': {'a': 12},
            },
            'aBC': 123,
            'AbC': 3,
        })


class UrlTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.full_path = reverse(name='test-url')
        self.full_path_with_pk = reverse(name='test-url-pk', kwargs={'pk': 1})
        self.expected_full_path = '{API_URL}{relative_url}'.format(API_URL=API_URL, relative_url='/test/url/')
        self.expected_full_path_with_pk = '{API_URL}{relative_url}'.format(API_URL=API_URL, relative_url='/test/url/1/')

    def test_reverse(self):
        self.assertEqual(self.full_path, self.expected_full_path)
        self.assertEqual(self.expected_full_path_with_pk, self.expected_full_path_with_pk)

