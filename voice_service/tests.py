from django.test import TestCase
from voice_service.google.intents import Intent, yes_intent, no_intent
from voice_service.google.tts import tts, tts_to_s3
from unittest.mock import patch
from mock import mock_open


class _Response:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class IntentsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sample_intent = Intent(name='sample_intent',
                                   samples=['one', 'two', 'three', 'forty five'])

    def test_intent_attrs(self):
        self.assertEqual(self.sample_intent.name, 'sample_intent')
        self.assertListEqual(self.sample_intent.samples, ['one', 'two', 'three', 'forty five'])

    def test_match(self):
        self.assertTrue(self.sample_intent.is_match('one'))
        self.assertTrue(self.sample_intent.is_match('three'))
        self.assertTrue(self.sample_intent.is_match('forty five'))

        self.assertFalse(self.sample_intent.is_match(''))
        self.assertFalse(self.sample_intent.is_match('o'))
        self.assertFalse(self.sample_intent.is_match('forty fives'))
        self.assertFalse(self.sample_intent.is_match('forty six'))

    def test_yes_intent(self):
        self.assertEqual(yes_intent.name, 'yes')
        self.assertTrue(yes_intent.is_match('hell yes'))
        self.assertTrue(yes_intent.is_match('hell yeah'))
        self.assertFalse(yes_intent.is_match('hell yooo'))

    def test_no_intent(self):
        self.assertEqual(no_intent.name, 'no')
        self.assertTrue(no_intent.is_match('nope'))
        self.assertTrue(no_intent.is_match('definitely not'))
        self.assertFalse(no_intent.is_match('definitely doughnut'))


class TtsTestCases(TestCase):
    def test_raise_none_text_ssml(self):
        with self.assertRaises(ValueError):
            tts()

    def test_raise_both_text_ssml(self):
        with self.assertRaises(ValueError):
            tts(text='hello', ssml='hello')

    @patch('voice_service.google.tts.types')
    @patch('voice_service.google.tts.TextToSpeechClient')
    def test_tts(self, mock_tts_client, mock_types):
        def _synthesize_speech(*args, **kwargs):
            return _Response(audio_content=str.encode('some-audio-content-here'))

        def _dummy(*args, **kwargs):
            return {}

        mock_tts_client.return_value = _Response(synthesize_speech=_synthesize_speech)
        mock_types.return_value = _Response(SynthesisInput=_dummy,
                                            VoiceSelectionParams=_dummy,
                                            AudioConfig=_dummy)

        m_open = mock_open()
        with patch('voice_service.google.tts.open', m_open):
            filename, local_file_path = tts(text='This is a sample content!')

        m_open.assert_called_once_with(local_file_path, 'wb')
        handle = m_open()
        handle.write.assert_called_once_with(str.encode('some-audio-content-here'))
        self.assertTrue(filename.endswith('.mp3'))
        self.assertTrue(local_file_path.startswith('/tmp/'))

    @patch('voice_service.google.tts.boto3_client')
    @patch('voice_service.google.tts.tts')
    def test_tts_to_s3(self, mock_tts, mock_boto3_client):
        def _upload_file(*args, **kwargs):
            return

        mock_tts.return_value = 'a-file.mp3', '/tmp/a-file.mp3'
        mock_boto3_client.return_value = _Response(upload_file=_upload_file)

        file_key = tts_to_s3('key', text='Yesterday, all my trouble seems so far away!')
        self.assertEqual(file_key, 'tts/a-file.mp3')

    @patch('voice_service.google.tts.boto3_client')
    @patch('voice_service.google.tts.tts')
    def test_tts_to_s3_url(self, mock_tts, mock_boto3_client):
        def _upload_file(*args, **kwargs):
            return

        mock_tts.return_value = 'a-file.mp3', '/tmp/a-file.mp3'
        mock_boto3_client.return_value = _Response(upload_file=_upload_file)

        url = tts_to_s3('url', text='Yesterday, all my trouble seems so far away!')
        self.assertEqual(url, 'https://s3-us-west-1.amazonaws.com/caressa-prod/tts/a-file.mp3')
