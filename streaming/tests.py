import boto3

from uuid import uuid4
from django.test import TestCase, RequestFactory
from model_mommy import mommy
from alexa.models import UserSettings, User
from streaming.models import Tag, AudioFile, UserMainContentConsumption, UserContentRepository
from streaming.views import stream_io
from streaming.test_helper_functions import request_body_creator_for_intent, \
    request_body_creator, request_body_creator_for_audio_player, request_body_creator_for_pause_command
from django.db.models import signals


class UserContentRepositoryTests(TestCase):
    def test_save_for_user(self):
        user_one = mommy.make('alexa.user', user_type=User.CARETAKER,
                              email='user@example.com', )
        user_two = mommy.make('alexa.user', user_type=User.CARETAKER,
                              email='user2@example.com', )

        UserContentRepository.save_for_user(user_one, injected_content_repository=[{'a': 1, 'b': 2}])
        UserContentRepository.save_for_user(user_two)

        repository1 = UserContentRepository.objects.filter(user=user_one).all()[0]
        repository2 = UserContentRepository.objects.filter(user=user_two).all()[0]

        self.assertEqual(repository1.injected_content_repository, [{'a': 1, 'b': 2}])
        self.assertEqual(repository2.injected_content_repository, [])

        UserContentRepository.save_for_user(user_one, injected_content_repository=[{'a': 3}])

        repository3 = UserContentRepository.objects.filter(user=user_one).all()[0]
        self.assertEqual(repository3.injected_content_repository, [{'a': 3}])

    def test_assert_save_for_non_senior(self):
        user_one = mommy.make('alexa.user', email='user@example.com', user_type=User.FAMILY)
        with self.assertRaises(AssertionError):
            UserContentRepository.save_for_user(user_one, injected_content_repository=[])

        user_two = mommy.make('alexa.user', email='user2@example.com', user_type=User.CAREGIVER)
        with self.assertRaises(AssertionError):
            UserContentRepository.save_for_user(user_two, injected_content_repository=[])

        user_three = mommy.make('alexa.user', email='user3@example.com', user_type=User.CAREGIVER_ORG)
        with self.assertRaises(AssertionError):
            UserContentRepository.save_for_user(user_three, injected_content_repository=[])

    def test_get_for_user(self):
        user_one = mommy.make('alexa.user', email='user@example.com', user_type=User.CARETAKER)
        self.assertEqual(UserContentRepository.get_for_user(user_one).injected_content_repository, [])

    def test_assert_get_for_non_senior(self):
        user_one = mommy.make('alexa.user', email='user@example.com', user_type=User.FAMILY)
        with self.assertRaises(AssertionError):
            UserContentRepository.get_for_user(user_one)

        user_two = mommy.make('alexa.user', email='user2@example.com', user_type=User.CAREGIVER)
        with self.assertRaises(AssertionError):
            UserContentRepository.get_for_user(user_two,)

        user_three = mommy.make('alexa.user', email='user3@example.com', user_type=User.CAREGIVER_ORG)
        with self.assertRaises(AssertionError):
            UserContentRepository.get_for_user(user_three)


class TagModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        signals.pre_save.disconnect(receiver=AudioFile.pre_save_operations,
                                    sender=AudioFile,
                                    dispatch_uid='audio_file.pre_save')

        cls.tag1 = mommy.make('streaming.Tag', name='song-classical', is_setting_available=False)  # type: Tag
        cls.default_tag1 = mommy.make('streaming.Tag', is_setting_available=True)  # type: Tag
        cls.default_tag2 = mommy.make('streaming.Tag', is_setting_available=True)   # type: Tag

        cls.audio_file1 = mommy.make('streaming.AudioFile')  # type: AudioFile
        cls.audio_file1.tags.add(cls.tag1)

        tag_irrelevant = mommy.make('streaming.Tag', name='irrelevant', is_setting_available=False)  # type: Tag
        cls.audio_file2 = mommy.make('streaming.AudioFile')  # type: AudioFile
        cls.audio_file3 = mommy.make('streaming.AudioFile')  # type: AudioFile

        cls.audio_file2.tags.add(tag_irrelevant)
        cls.audio_file3.tags.add(tag_irrelevant)

        cls.tag_multi1 = mommy.make('streaming.Tag', name='song-tag-1', is_setting_available=False)  # type: Tag
        cls.tag_multi2 = mommy.make('streaming.Tag', name='song-tag-2', is_setting_available=False)  # type: Tag

        cls.audio_file_multi_tagged = mommy.make('streaming.AudioFile')  # type: AudioFile
        cls.audio_file_multi_tagged.tags.add(cls.tag_multi1)
        cls.audio_file_multi_tagged.tags.add(cls.tag_multi2)

        cls.same_tag_audio_file1 = mommy.make('streaming.AudioFile')     # type: AudioFile
        cls.same_tag_audio_file2 = mommy.make('streaming.AudioFile')     # type: AudioFile

        cls.tag_for_multi_audio = mommy.make('streaming.Tag',                # type: Tag
                                             name='multi-audio',
                                             is_setting_available=False)
        cls.tag_for_only_first = mommy.make('streaming.Tag',                 # type: Tag
                                            name='multi-audio-but-only-first',
                                            is_setting_available=False)

        cls.same_tag_audio_file1.tags.add(cls.tag_for_multi_audio)
        cls.same_tag_audio_file1.tags.add(cls.tag_for_only_first)
        cls.same_tag_audio_file2.tags.add(cls.tag_for_multi_audio)

        cls.audio_file_default_tagged = mommy.make('streaming.AudioFile')  # type: AudioFile
        cls.audio_file_default_tagged_2 = mommy.make('streaming.AudioFile')  # type: AudioFile
        cls.audio_file_default_tagged_3 = mommy.make('streaming.AudioFile')  # type: AudioFile
        cls.audio_file_default_tagged.tags.add(cls.default_tag1)
        cls.audio_file_default_tagged_2.tags.add(cls.default_tag2)
        cls.audio_file_default_tagged_3.tags.add(cls.default_tag1)
        cls.audio_file_default_tagged_3.tags.add(cls.default_tag2)

    def test_tag_list_to_audio_file(self):
        tag_list = [self.tag1.id]
        tag_list_2 = [self.tag1.id, 300, 400]
        audio_file_fetched = Tag.tag_list_to_audio_file(tag_list)
        audio_file_fetched_2 = Tag.tag_list_to_audio_file(tag_list_2)

        self.assertTrue(self.audio_file1.tags.all().count() == 1)
        self.assertEqual(audio_file_fetched, self.audio_file1)
        self.assertEqual(audio_file_fetched_2, self.audio_file1)

    def test_empty_tag_list_to_audio_file(self):
        empty_tag_list = []
        audio_file_fetched = Tag.tag_list_to_audio_file(empty_tag_list)
        self.assertIn(audio_file_fetched, [self.audio_file_default_tagged,
                                           self.audio_file_default_tagged_2,
                                           self.audio_file_default_tagged_3])

    def test_tag_string_to_audio_with_multiple_tag(self):
        audio_file_fetched = Tag.tag_list_to_audio_file([self.tag_multi1.id])
        audio_file_fetched_2 = Tag.tag_list_to_audio_file([self.tag_multi2.id])
        audio_file_fetched3 = Tag.tag_list_to_audio_file([self.tag_multi1.id, self.tag_multi2.id])

        self.assertTrue(self.audio_file_multi_tagged.tags.all().count() == 2)
        self.assertEqual(audio_file_fetched, self.audio_file_multi_tagged)
        self.assertEqual(audio_file_fetched_2, self.audio_file_multi_tagged)
        self.assertEqual(audio_file_fetched3, self.audio_file_multi_tagged)

    def test_same_tag_multi_audio(self):
        audio_file_fetched = Tag.tag_list_to_audio_file([self.tag_for_multi_audio.id])
        self.assertIn(audio_file_fetched, [self.same_tag_audio_file1, self.same_tag_audio_file2])

        audio_file_fetched2 = Tag.tag_list_to_audio_file([self.tag_for_only_first.id])
        self.assertEqual(audio_file_fetched2, self.same_tag_audio_file1)

    def test_default_tags_list(self):
        default_tag_list = Tag.default_tags_list()
        created_default_tags = [self.default_tag1.id, self.default_tag2.id]

        self.assertGreater(len(default_tag_list), 0)
        self.assertEqual(default_tag_list, created_default_tags)

    def test_string_representation(self):
        self.assertEqual(str(self.tag1), 'song-classical')
        self.assertEqual(str(self.tag_multi1), 'song-tag-1')


class AudioFileModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        signals.pre_save.disconnect(sender=AudioFile,
                                    dispatch_uid='audio_file.pre_save')
        cls.audio_file1 = mommy.make('streaming.AudioFile',  # type: AudioFile
                                     duration=40,
                                     audio_type=AudioFile.TYPE_SONG,
                                     name='song name'
                                     )
        cls.audio_file2 = mommy.make('streaming.AudioFile',  # type: AudioFile
                                     duration=100,
                                     )

    def test_url_hyperlink(self):
        created_html = "<a href='{url}' target='_blank'>{url}</a>".format(url=self.audio_file1.url)
        format_html = self.audio_file1.url_hyperlink()

        self.assertEqual(created_html, format_html)

    def test_duration_in_minutes(self):
        duration_in_minutes1 = self.audio_file1.duration_in_minutes
        duration_in_minutes2 = self.audio_file2.duration_in_minutes
        expected_duration1 = '40 sec(s)'
        expected_duration2 = '01 min(s) 40 sec(s)'

        self.assertEqual(duration_in_minutes1, expected_duration1)
        self.assertEqual(duration_in_minutes2, expected_duration2)

    def test_is_publicly_accessible(self):
        signals.pre_save.connect(receiver=AudioFile.pre_save_operations,
                                 sender=AudioFile,
                                 dispatch_uid='_in-test-signal-connect')
        bucket_name = 'caressa-test-{uuid}'.format(uuid=str(uuid4())[:8])
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket_name)
        file_path = 'streaming/sample_files/sample_audio.mp3'
        file_name = 'sample_audio.mp3'

        s3.upload_file(file_path, bucket_name, file_name, ExtraArgs={'ACL': 'public-read'})

        audio_type = 'TestAudioType1'
        url = '{s3}/{bucket_name}/{file_name}'.format(s3='https://s3.amazonaws.com',
                                                      bucket_name=bucket_name,
                                                      file_name=file_name)
        name = 'TestAudioFile1'
        description = 'TestDescription1'

        sample_audio_file = AudioFile(audio_type=audio_type,
                                      url=url,
                                      name=name,
                                      description=description)
        sample_audio_file.save()
        is_public = sample_audio_file.is_publicly_accessible()

        self.assertIsInstance(sample_audio_file.duration, int)
        self.assertIsNotNone(sample_audio_file.hash)
        self.assertTrue(is_public)

        bucket = boto3.resource('s3').Bucket(bucket_name)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()

        signals.pre_save.disconnect(sender=AudioFile,
                                    dispatch_uid='_in-test-signal-connect')

    def test_string_representation(self):
        actual_string_representation = str(self.audio_file1)
        self.assertEqual(actual_string_representation, "(song) song name")


class StreamingPlayTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = mommy.make('alexa.User', user_type=User.CARETAKER)
        cls.user2 = mommy.make('alexa.User', user_type=User.CARETAKER)

        cls.tag1 = mommy.make('streaming.Tag', is_setting_available=False)
        cls.tag2 = mommy.make('streaming.Tag', is_setting_available=False)
        cls.tag3 = mommy.make('streaming.Tag', is_setting_available=True)

        cls.user_settings = mommy.make(UserSettings, user=cls.user, data={"genres": [cls.tag1.id, cls.tag2.id]})

        cls.audio_file_1 = mommy.make('streaming.AudioFile',
                                      make_m2m=False,
                                      url='http://www.example.com/audio/song1.mp3',
                                      )
        cls.audio_file_2 = mommy.make('streaming.AudioFile',
                                      make_m2m=True,
                                      tags=[cls.tag1],
                                      url='http://www.example.com/audio/song2.mp3',
                                      )
        cls.audio_file_3 = mommy.make('streaming.AudioFile',
                                      make_m2m=True,
                                      tags=[cls.tag1, cls.tag2],
                                      url='http://www.example.com/audio/song3.mp3',
                                      )
        cls.audio_file_4 = mommy.make('streaming.AudioFile',
                                      make_m2m=True,
                                      tags=[cls.tag3],
                                      url='http://www.example.com/audio/song4.mp3',
                                      )

    def test_launch_request(self):
        request_body = request_body_creator('LaunchRequest')
        request = self.factory.get('/streaming')
        request.user = self.user

        data = stream_io(request_body, request)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        possible_audio_url_list = [self.audio_file_2.url, self.audio_file_3.url]

        self.assertIn(response_audio_url, possible_audio_url_list)

    def test_launch_request_without_settings(self):
        request_body = request_body_creator('LaunchRequest')
        request = self.factory.get('/streaming')
        request.user = self.user2

        data = stream_io(request_body, request)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        audio_url = self.audio_file_4.url

        self.assertEqual(response_audio_url, audio_url)
        self.assertNotEqual(response_audio_url, self.audio_file_1.url)

    def test_play_command(self):
        request_body = request_body_creator('PlaybackController.PlayCommandIssued')
        request = self.factory.get('/streaming')
        request.user = self.user

        data = stream_io(request_body, request)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        possible_audio_url_list = [self.audio_file_2.url, self.audio_file_3.url]

        self.assertIn(response_audio_url, possible_audio_url_list)
        self.assertNotEqual(response_audio_url, self.audio_file_1.url)

    def test_next_command(self):
        request_body = request_body_creator('PlaybackController.NextCommandIssued')
        request = self.factory.get('/streaming')
        request.user = self.user

        data = stream_io(request_body, request)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        possible_audio_url_list = [self.audio_file_2.url, self.audio_file_3.url]

        self.assertIn(response_audio_url, possible_audio_url_list)
        self.assertNotEqual(response_audio_url, self.audio_file_1.url)

    def test_resume_intent(self):
        request_body = request_body_creator_for_intent('AMAZON.ResumeIntent')
        request = self.factory.get('/streaming')
        request.user = self.user

        data = stream_io(request_body, request)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        possible_audio_url_list = [self.audio_file_2.url, self.audio_file_3.url]

        self.assertIn(response_audio_url, possible_audio_url_list)
        self.assertNotEqual(response_audio_url, self.audio_file_1.url)

    def test_next_intent(self):
        request_body = request_body_creator_for_intent('AMAZON.NextIntent')
        request = self.factory.get('/streaming')
        request.user = self.user

        data = stream_io(request_body, request)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        possible_audio_url_list = [self.audio_file_2.url, self.audio_file_3.url]

        self.assertIn(response_audio_url, possible_audio_url_list)
        self.assertNotEqual(response_audio_url, self.audio_file_1.url)

    def test_playback_started_request(self):
        umcc_count_before_save_state = UserMainContentConsumption.objects.all().count()
        self.assertEqual(umcc_count_before_save_state, 0)

        token = self.audio_file_1.id

        request_body = request_body_creator_for_audio_player('AudioPlayer.PlaybackStarted', token)
        request = self.factory.get('/streaming')
        request.user = self.user
        stream_io(request_body, request)

        consumed_audio_by_user = UserMainContentConsumption.objects.all()[0].played_main_content
        umcc_count_after_save_state = UserMainContentConsumption.objects.all().count()

        self.assertEqual(consumed_audio_by_user, self.audio_file_1)
        self.assertEqual(umcc_count_after_save_state, 1)


class StreamingNextAndQueueTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = mommy.make('alexa.User', user_type=User.CARETAKER)
        cls.tag1 = mommy.make('streaming.Tag')

        cls.user_settings = mommy.make(UserSettings, user=cls.user, data={"genres": [cls.tag1.id]})

        cls.audio_file_1 = mommy.make('streaming.AudioFile',
                                      make_m2m=True,
                                      tags=[cls.tag1],
                                      url='http://www.example.com/audio/song2.mp3',
                                      )

    def test_nearly_finished_request(self):
        token = self.audio_file_1.id
        request_nearly_finished = request_body_creator_for_audio_player('AudioPlayer.PlaybackNearlyFinished', token)
        request = self.factory.get('/streaming')

        request.user = self.user
        data = stream_io(request_nearly_finished, request)

        expected_url = self.audio_file_1.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']

        self.assertEqual(expected_url, response_url)


class StreamingPauseAndFillerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = mommy.make('alexa.User', user_type=User.CARETAKER)
        cls.tag1 = mommy.make('streaming.Tag')
        cls.audio_file_1 = mommy.make('streaming.AudioFile',
                                      make_m2m=True,
                                      tags=[cls.tag1],
                                      url='http://www.example.com/audio/song2.mp3',
                                      )

    def test_pause_command(self):
        token = self.audio_file_1
        request_body_pause_command = request_body_creator_for_pause_command(token)
        request = self.factory.get('/streaming')
        request.user = self.user
        data = stream_io(request_body_pause_command, request)
        audio_player_directive = data['response']['directives'][0]['type']

        self.assertEqual(audio_player_directive, 'AudioPlayer.Stop')

    def test_pause_intent(self):
        request_body_pause_intent = request_body_creator_for_intent('AMAZON.PauseIntent')
        request = self.factory.get('/streaming')
        request.user = self.user
        data = stream_io(request_body_pause_intent, request)
        audio_player_directive = data['response']['directives'][0]['type']
        self.assertEqual(audio_player_directive, 'AudioPlayer.Stop')

    def test_none_intent(self):
        none_intent = request_body_creator_for_intent('None_Intent')
        request = self.factory.get('/streaming')
        request.user = self.user
        data = stream_io(none_intent, request)
        audio_player_directive = data['response']['directives'][0]['type']
        self.assertEqual(audio_player_directive, 'AudioPlayer.Stop')

    def test_fallback_filler(self):
        fallback_request = request_body_creator('fallback')
        request = self.factory.get('/streaming')
        request.user = self.user
        data = stream_io(fallback_request, request)
        self.assertDictEqual(data, {'result': 'success'})
