from django.test import TestCase
from mock import patch
from model_mommy import mommy
from streaming.models import Tag, AudioFile, audio_file_accessibility_and_duration, Playlist, PlaylistHasAudio,\
    UserPlaylistStatus, TrackingAction
from streaming.views import stream_io
from alexa.models import AUser, Session
from django.db.models import signals
import datetime
import boto3
from random import randint
from streaming.test_helper_functions import request_body_creator_for_next_command, request_body_creator_for_intent, \
    request_body_creator, request_body_creator_for_audio_player, request_body_creator_for_pause_command
import botocore


class TagModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        tag1 = mommy.make(Tag, name='song-classical')
        cls.user_one = mommy.make_recipe('alexa.user')
        cls.context = {'user': cls.user_one}
        cls.audio_file1 = mommy.make_recipe('streaming.audio_file_recipe')  # type: AudioFile
        cls.audio_file1.tags.add(tag1)

        tag_irrelevant = mommy.make(Tag, name='irrelevant')
        cls.audio_file2 = mommy.make_recipe('streaming.audio_file_recipe')  # type: AudioFile
        cls.audio_file3 = mommy.make_recipe('streaming.audio_file_recipe')  # type: AudioFile

        cls.audio_file2.tags.add(tag_irrelevant)
        cls.audio_file3.tags.add(tag_irrelevant)

        tag_multi1 = mommy.make(Tag, name='song-tag-1')
        tag_multi2 = mommy.make(Tag, name='song-tag-2')

        cls.audio_file_multi_tagged = mommy.make_recipe('streaming.audio_file_recipe')  # type: AudioFile
        cls.audio_file_multi_tagged.tags.add(tag_multi1)
        cls.audio_file_multi_tagged.tags.add(tag_multi2)

        cls.same_tag_audio_file1 = mommy.make_recipe('streaming.audio_file_recipe')     # type: AudioFile
        cls.same_tag_audio_file2 = mommy.make_recipe('streaming.audio_file_recipe')     # type: AudioFile

        tag_for_multi_audio = mommy.make(Tag, name='multi-audio')
        tag_for_only_first = mommy.make(Tag, name='multi-audio-but-only-first')

        cls.same_tag_audio_file1.tags.add(tag_for_multi_audio)
        cls.same_tag_audio_file1.tags.add(tag_for_only_first)
        cls.same_tag_audio_file2.tags.add(tag_for_multi_audio)

    def test_tag_string_to_audio_file(self):
        tag_str = 'song-classical'
        audio_file_fetched = Tag.string_to_audio_file(tag_str, self.context)
        self.assertEqual(audio_file_fetched, self.audio_file1)

        tag_str2 = 'song-jazz, song-classical, song-meaningless-tag'
        audio_file_fetched = Tag.string_to_audio_file(tag_str2, self.context)
        self.assertEqual(audio_file_fetched, self.audio_file1)

        tag_str3 = 'song-jazz,song-classical,song-meaningless-tag'
        audio_file_fetched = Tag.string_to_audio_file(tag_str3, self.context)
        self.assertEqual(audio_file_fetched, self.audio_file1)

    def test_tag_string_to_none(self):
        tag_str = 'song-meaningless-tag, song-another-meaningless-tag2'
        audio_file_fetched = Tag.string_to_audio_file(tag_str, self.context)
        self.assertIsNone(audio_file_fetched, 'If no matching tag in audio files it leads to None')

    def test_tag_string_to_audio_with_multiple_tag(self):
        audio_file_fetched = Tag.string_to_audio_file('song-tag-1', self.context)
        self.assertEqual(audio_file_fetched, self.audio_file_multi_tagged)

        audio_file_fetched2 = Tag.string_to_audio_file('song-tag-1,x,y,z', self.context)
        self.assertEqual(audio_file_fetched2, self.audio_file_multi_tagged)

        audio_file_fetched3 = Tag.string_to_audio_file('xxx,yyy,song-tag-1,zzz', self.context)
        self.assertEqual(audio_file_fetched3, self.audio_file_multi_tagged)

        audio_file_fetched4 = Tag.string_to_audio_file('xxx,song-tag-1,yyy,zzz,song-tag-2,ttt', self.context)
        self.assertEqual(audio_file_fetched4, self.audio_file_multi_tagged)

        audio_file_fetched5 = Tag.string_to_audio_file('zzz,song-tag-2', self.context)
        self.assertEqual(audio_file_fetched5, self.audio_file_multi_tagged)

        audio_file_fetched6 = Tag.string_to_audio_file('xxx,yyy,zzz', self.context)
        self.assertIsNone(audio_file_fetched6)

    def test_same_tag_multi_audio(self):

        audio_file_fetched = Tag.string_to_audio_file('multi-audio', self.context)
        self.assertIn(audio_file_fetched, [self.same_tag_audio_file1, self.same_tag_audio_file2])

        audio_file_fetched2 = Tag.string_to_audio_file('multi-audio-but-only-first', self.context)
        self.assertEqual(audio_file_fetched2, self.same_tag_audio_file1)


class AudioFileModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        signals.pre_save.disconnect(receiver=audio_file_accessibility_and_duration,
                                    sender=AudioFile, dispatch_uid='audio_file_accessibility_and_duration')
        cls.audio_file1 = mommy.make_recipe('streaming.audio_file_recipe', duration=40)  # type: AudioFile
        cls.audio_file2 = mommy.make_recipe('streaming.audio_file_recipe', duration=100)  # type: AudioFile

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
        signals.pre_save.connect(receiver=audio_file_accessibility_and_duration,
                                 sender=AudioFile,
                                 dispatch_uid='audio_file_accessibility_and_duration')
        bucket_name = 'caressa-test-{random_number}'.format(random_number=randint(1, 100000))
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
        self.assertTrue(is_public)

        bucket = boto3.resource('s3').Bucket(bucket_name)
        for key in bucket.objects.all():
            key.delete()
        bucket.delete()

    def test_string_representation(self):
        actual_string_representation = str(self.audio_file1)
        expected_string_representation = "({audio_type}) {file_name}".format(audio_type=self.audio_file1.audio_type,
                                                                             file_name=self.audio_file1.name)

        self.assertEqual(actual_string_representation, expected_string_representation)


class PlaylistModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        signals.pre_save.disconnect(receiver=audio_file_accessibility_and_duration,
                                    sender=AudioFile, dispatch_uid='audio_file_accessibility_and_duration')
        cls.playlist_has_audio = mommy.make_recipe('streaming.playlist_has_audio_recipe')  # type: PlaylistHasAudio
        cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe', duration=40)  # type: AudioFile

    def test_getting_audio_files(self):
        first_audio_file_in_playlist = self.playlist_has_audio.playlist.get_audio_files()[0].name
        self.playlist_has_audio.playlist.add_audio_file(self.audio_file_1)
        first_audio_file_name = 'song1'

        self.assertEqual(first_audio_file_in_playlist, first_audio_file_name)

    def test_adding_audio_file(self):
        audio_file_count = self.playlist_has_audio.playlist.get_audio_files().count()
        self.playlist_has_audio.playlist.add_audio_file(self.audio_file_1)
        added_audio_file_count = self.playlist_has_audio.playlist.get_audio_files().count()

        self.assertGreater(added_audio_file_count, audio_file_count)

    def test_total_duration(self):
        duration = 53
        self.playlist_has_audio.playlist.add_audio_file(self.audio_file_1)
        total_duration = self.playlist_has_audio.playlist.total_duration

        self.assertEqual(duration, total_duration)

    def test_number_of_audio(self):
        audio_count = self.playlist_has_audio.playlist.number_of_audio
        self.playlist_has_audio.playlist.add_audio_file(self.audio_file_1)
        added_audio_file_count = self.playlist_has_audio.playlist.get_audio_files().count()

        self.assertEqual(1, audio_count)
        self.assertEqual(2, added_audio_file_count)

    def test_get_default(self):

        Playlist.DEFAULT_PLAYLIST_NAME = 'playlist'
        self.assertRaises(Exception, Playlist.get_default)

        Playlist.DEFAULT_PLAYLIST_NAME = 'cold-start'
        fetched_default_name = str(Playlist.get_default())
        expected_default_name = str(Playlist.objects.all()[0])

        self.assertEqual(fetched_default_name, expected_default_name)

    def test_string_representation(self):
        fetched_string_representation = str(Playlist.objects.all()[0])
        expected_string_representation = "{name} (duration: {duration}," \
                                         " #files: {num_files})".format(name='cold-start',
                                                                        duration='13 sec(s)',
                                                                        num_files=1, )

        self.assertEqual(fetched_string_representation, expected_string_representation)


class PlaylistHasAudioModelTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):

        tag1 = mommy.make(Tag, name='song-classical')
        cls.playlist_has_audio = mommy.make_recipe('streaming.playlist_has_audio_recipe')
        cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')

        cls.playlist_has_audio.playlist.add_audio_file(cls.audio_file_1)    # Only Song Name

        cls.playlist_has_audio.playlist.add_audio_file(cls.audio_file_1)    # Song Name and Tag
        play_list_has_audio_2 = PlaylistHasAudio.objects.all()[1]
        play_list_has_audio_2.tag = 'song-classical'
        play_list_has_audio_2.save()

        cls.playlist_has_audio.playlist.add_audio_file(cls.audio_file_1)    # Only Tag
        play_list_has_audio_3 = PlaylistHasAudio.objects.all()[2]
        play_list_has_audio_3.tag = 'song-classical'
        play_list_has_audio_3.audio = None
        play_list_has_audio_3.save()
        cls.audio_file_2.tags.add(tag1)

        cls.current_day_time_patch = patch('streaming.models.PlaylistHasAudio._current_daytime')
        cls.mock_current_day_time = cls.current_day_time_patch.start()
        cls.mock_current_day_time.return_value = 'morning'
        cls.tomorrow = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        cls.day_time_list = ['morning', 'afternoon']
        cls.next_day_time = 'afternoon'

    def test_hash_creation(self):
        hash_01 = PlaylistHasAudio.objects.all()[0].hash
        hash_02 = PlaylistHasAudio.objects.all()[1].hash
        hash_03 = PlaylistHasAudio.objects.all()[2].hash

        self.assertNotEqual(hash_01, hash_02)
        self.assertNotEqual(hash_02, hash_03)

    def test_get_audio_with_static_audio_only(self):
        playlist_has_audio_1_instance = PlaylistHasAudio.objects.all()[0]
        playlist_has_audio_fetched_audio = playlist_has_audio_1_instance .get_audio()
        playlist_has_audio_fetched_audio_name = playlist_has_audio_fetched_audio.name

        self.assertIsNotNone(playlist_has_audio_1_instance.audio)
        self.assertEqual(playlist_has_audio_1_instance.tag, '')
        self.assertIsInstance(playlist_has_audio_fetched_audio, AudioFile)
        self.assertEqual(playlist_has_audio_fetched_audio_name, 'song1')

    def test_get_audio_with_static_audio_and_tag(self):
        playlist_has_audio_2_instance = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_fetched_audio = playlist_has_audio_2_instance.get_audio()
        playlist_has_audio_fetched_audio_name = playlist_has_audio_fetched_audio.name

        self.assertIsInstance(playlist_has_audio_2_instance, PlaylistHasAudio)
        self.assertIsNotNone(playlist_has_audio_2_instance.audio)
        self.assertIsNotNone(playlist_has_audio_2_instance.tag)
        self.assertNotEqual(playlist_has_audio_2_instance.tag, '')
        self.assertIsInstance(playlist_has_audio_fetched_audio, AudioFile)
        self.assertEqual(playlist_has_audio_fetched_audio_name, 'song2')

    def test_get_audio_with_tag_only(self):
        playlist_has_audio_3_instance = PlaylistHasAudio.objects.all()[2]
        playlist_has_audio_fetched_audio = playlist_has_audio_3_instance.get_audio()
        playlist_has_audio_fetched_audio_name = playlist_has_audio_fetched_audio.name

        self.assertIsNone(playlist_has_audio_3_instance.audio)
        self.assertIsNotNone(playlist_has_audio_3_instance.tag)
        self.assertNotEqual(playlist_has_audio_3_instance.tag, '')
        self.assertEqual(playlist_has_audio_3_instance.tag, 'song-classical')
        self.assertIsInstance(playlist_has_audio_fetched_audio, AudioFile)
        self.assertEqual(playlist_has_audio_fetched_audio_name, 'song3')

    def test_next_no_date_no_time(self):
        current_playlist_has_audio = PlaylistHasAudio.objects.all()[0]
        second_playlist_has_audio = self.playlist_has_audio.next()
        third_playlist_has_audio = second_playlist_has_audio.next()

        self.assertNotEqual(current_playlist_has_audio, second_playlist_has_audio)
        self.assertNotEqual(current_playlist_has_audio.order_id, second_playlist_has_audio.order_id)
        self.assertNotEqual(third_playlist_has_audio.order_id, second_playlist_has_audio.order_id)

    def test_next_only_date_no_time(self):
        playlist_has_audio_2 = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_2_with_date = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_2_with_date.play_date = self.tomorrow
        playlist_has_audio_2_with_date.save()
        next_playlist_has_audio = self.playlist_has_audio.next()

        self.assertNotEqual(playlist_has_audio_2_with_date.play_date, playlist_has_audio_2.play_date)
        self.assertNotEqual(playlist_has_audio_2, next_playlist_has_audio)
        self.assertNotEqual(playlist_has_audio_2.order_id, next_playlist_has_audio.order_id)

    def test_next_no_date_only_time(self):
        playlist_has_audio_2 = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_2_with_time = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_2_with_time.play_time = self.next_day_time
        playlist_has_audio_2_with_time.save()
        next_playlist_has_audio = self.playlist_has_audio.next()

        self.assertNotEqual(playlist_has_audio_2_with_time.play_time, playlist_has_audio_2.play_time)
        self.assertNotEqual(playlist_has_audio_2, next_playlist_has_audio)
        self.assertNotEqual(playlist_has_audio_2.order_id, next_playlist_has_audio.order_id)

    def test_next_date_and_time(self):
        playlist_has_audio_2 = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_2_with_time_and_date = PlaylistHasAudio.objects.all()[1]
        playlist_has_audio_2_with_time_and_date.play_time = self.next_day_time
        playlist_has_audio_2_with_time_and_date.play_date = self.tomorrow
        playlist_has_audio_2_with_time_and_date.save()
        next_playlist_has_audio = self.playlist_has_audio.next()

        self.assertNotEqual(playlist_has_audio_2_with_time_and_date.play_time, playlist_has_audio_2.play_time)
        self.assertNotEqual(playlist_has_audio_2_with_time_and_date.play_date, playlist_has_audio_2.play_date)
        self.assertNotEqual(playlist_has_audio_2, next_playlist_has_audio)
        self.assertNotEqual(playlist_has_audio_2.order_id, next_playlist_has_audio.order_id)


class UserPlaylistStatusModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_playlist_status_1 = mommy.make_recipe('streaming.user_playlist_status_recipe')
        cls.user_playlist_status_2 = mommy.make_recipe('streaming.user_playlist_status_recipe')
        cls.user_playlist_status_3 = mommy.make_recipe('streaming.user_playlist_status_recipe')
        cls.user_1 = cls.user_playlist_status_1.user
        cls.user_2 = mommy.make_recipe('alexa.user')
        cls.audio_file1 = mommy.make_recipe('streaming.audio_file_recipe')  # type: AudioFile
        cls.user_playlist_status_1.playlist_has_audio.playlist.add_audio_file(cls.audio_file1)

    def test_ordering(self):

        qs = UserPlaylistStatus.objects.all()

        self.assertEqual(self.user_playlist_status_1, qs[0])
        self.assertEqual(self.user_playlist_status_2, qs[1])
        self.assertEqual(self.user_playlist_status_3, qs[2])

    def test_get_users_playlist(self):
        user_1_playlist = UserPlaylistStatus.get_users_playlist(self.user_1)
        user_2_playlist = UserPlaylistStatus.get_users_playlist(self.user_2)
        user_2_playlist_default = Playlist.get_default()

        self.assertIsNotNone(user_1_playlist)
        self.assertIsNotNone(user_2_playlist)
        self.assertIsInstance(user_1_playlist, Playlist)
        self.assertIsInstance(user_2_playlist, Playlist)
        self.assertEqual(user_2_playlist, user_2_playlist_default)

    def test_get_user_playlist_status_for_user(self):

        status_for_user_1, status_is_created_for_user_1 = self.user_playlist_status_1\
            .get_user_playlist_status_for_user(self.user_1)
        status_for_user_2, status_is_created_for_user_2 = self.user_playlist_status_1\
            .get_user_playlist_status_for_user(self.user_2)

        status_object_for_user_1 = UserPlaylistStatus.objects.all()[0]
        status_object_for_user_2 = UserPlaylistStatus.objects.all()[3]

        self.assertIsNotNone(status_for_user_1)
        self.assertIsNotNone(status_for_user_2)
        self.assertNotEqual(status_for_user_1, status_for_user_2)
        self.assertEqual(status_object_for_user_1, status_for_user_1)
        self.assertEqual(status_object_for_user_2, status_for_user_2)
        self.assertFalse(status_is_created_for_user_1)
        self.assertTrue(status_is_created_for_user_2)


class TrackingActionModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tracking_action_1 = mommy.make_recipe('streaming.tracking_action_recipe')
        cls.auser = AUser.objects.all()[0]
        cls.session = Session.objects.all()[0]
        cls.segment = 'TestSegment'

    def test_save_action_partial_segments(self):
        TrackingAction.save_action(self.auser, self.session, segment0=self.segment)
        action_count = TrackingAction.objects.all().count()
        segment0 = TrackingAction.objects.all()[1].segment0
        segment1 = TrackingAction.objects.all()[1].segment1

        self.assertIsNotNone(segment0)
        self.assertIsNone(segment1)
        self.assertEqual(action_count, 2)

    def test_save_action_full_segments(self):
        TrackingAction.save_action(self.auser,
                                   self.session,
                                   segment0=self.segment,
                                   segment1=self.segment,
                                   segment2=self.segment,
                                   segment3=self.segment,)
        action_count = TrackingAction.objects.all().count()
        segment0 = TrackingAction.objects.all()[1].segment0
        segment1 = TrackingAction.objects.all()[1].segment1
        segment2 = TrackingAction.objects.all()[1].segment2
        segment3 = TrackingAction.objects.all()[1].segment3

        self.assertIsNotNone(segment0)
        self.assertIsNotNone(segment1)
        self.assertIsNotNone(segment2)
        self.assertEqual(self.segment, segment3)
        self.assertEqual(action_count, 2)


class StreamingPlayTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.play_list_has_audio_1 = mommy.make_recipe('streaming.playlist_has_audio_recipe')
        cls.playlist_2 = mommy.make_recipe('streaming.playlist_recipe_2')   # second time user2 recipe runs

        cls.auser_2 = mommy.make(AUser,
                                 user=cls.playlist_2.user,
                                 alexa_user_id='TestAlexaUserId2',
                                 alexa_device_id='TestAlexaDeviceId2',
                                 engine_schedule='TestEngineSchedule', )

        cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_3 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.playlist_2.add_audio_file(cls.audio_file_1)
        cls.playlist_2.add_audio_file(cls.audio_file_2)
        cls.play_list_has_audio_1.playlist.add_audio_file(cls.audio_file_3)
        u = Playlist.objects.all()[0]  # to make sure default playlist have no user assigned
        u.user_id = None
        u.save()

    def test_cold_start_launch_request(self):
        request_body = request_body_creator(True, 'LaunchRequest')
        data = stream_io(request_body)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_url_from_db = AudioFile.objects.all()[0].url
        playlist_count = Playlist.objects.all().count()

        self.assertIsNone(Playlist.objects.all()[0].user_id)
        self.assertEqual(response_audio_url, expected_url_from_db)
        self.assertEqual(playlist_count, 2)

    def test_user_playlist_launch_request(self):
        request_body = request_body_creator(False, 'LaunchRequest')
        data = stream_io(request_body)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_url_from_db = AudioFile.objects.all()[1].url
        playlist_count = Playlist.objects.all().count()

        self.assertIsNotNone(Playlist.objects.all()[1].user_id)
        self.assertEqual(response_audio_url, expected_url_from_db)
        self.assertEqual(playlist_count, 2)

    def test_cold_start_play_command(self):
        request_body = request_body_creator(True, 'PlaybackController.PlayCommandIssued')
        data = stream_io(request_body)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_url_from_db = AudioFile.objects.all()[0].url
        playlist_count = Playlist.objects.all().count()

        self.assertIsNone(Playlist.objects.all()[0].user_id)
        self.assertEqual(response_audio_url, expected_url_from_db)
        self.assertEqual(playlist_count, 2)

    def test_user_playlist_play_command(self):
        request_body = request_body_creator(False, 'PlaybackController.PlayCommandIssued')
        data = stream_io(request_body)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_url_from_db = AudioFile.objects.all()[1].url
        playlist_count = Playlist.objects.all().count()

        self.assertIsNotNone(Playlist.objects.all()[1].user_id)
        self.assertEqual(response_audio_url, expected_url_from_db)
        self.assertEqual(playlist_count, 2)

    def test_cold_start_resume_intent(self):
        request_body = request_body_creator_for_intent(True, 'AMAZON.ResumeIntent')
        data = stream_io(request_body)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_url_from_db = AudioFile.objects.all()[0].url
        playlist_count = Playlist.objects.all().count()
        self.assertIsNone(Playlist.objects.all()[0].user_id)
        self.assertEqual(response_audio_url, expected_url_from_db)
        self.assertEqual(playlist_count, 2)

    def test_user_playlist_resume_intent(self):
        request_body = request_body_creator_for_intent(False, 'AMAZON.ResumeIntent')
        data = stream_io(request_body)
        response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_url_from_db = AudioFile.objects.all()[1].url
        playlist_count = Playlist.objects.all().count()

        self.assertIsNotNone(Playlist.objects.all()[1].user_id)
        self.assertEqual(response_audio_url, expected_url_from_db)
        self.assertEqual(playlist_count, 2)

    def test_cold_start_playback_started_request(self):

        ups_count_before_save_state = UserPlaylistStatus.objects.all().count()
        self.assertEqual(ups_count_before_save_state, 0)

        pha_object = type(self.play_list_has_audio_1).objects.all()[1]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
        data = stream_io(request_body)

        response = data['response']['shouldEndSession']
        ups_current_active_audio = UserPlaylistStatus.objects.all()[0].current_active_audio_id
        ups_count_after_save_state = UserPlaylistStatus.objects.all().count()

        self.assertEqual(ups_current_active_audio, pha_object.audio_id)
        self.assertEqual(ups_count_after_save_state, 1)
        self.assertTrue(response)

    def test_user_playlist_playback_started_request(self):
        ups_count_before_save_state = UserPlaylistStatus.objects.all().count()
        self.assertEqual(ups_count_before_save_state, 0)

        pha_object = type(self.play_list_has_audio_1).objects.all()[0]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
        data = stream_io(request_body)

        response = data['response']['shouldEndSession']
        ups_current_active_audio = UserPlaylistStatus.objects.all()[0].current_active_audio_id
        ups_count_after_save_state = UserPlaylistStatus.objects.all().count()

        self.assertEqual(ups_current_active_audio, pha_object.audio_id)
        self.assertEqual(ups_count_after_save_state, 1)
        self.assertTrue(response)


class StreamingNextAndQueueTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.play_list_has_audio_1 = mommy.make_recipe('streaming.playlist_has_audio_recipe')
        cls.playlist_2 = mommy.make_recipe('streaming.playlist_recipe_2')  # second time user2 recipe runs

        cls.auser_2 = mommy.make(AUser,
                                 user=cls.playlist_2.user,
                                 alexa_user_id='TestAlexaUserId2',
                                 alexa_device_id='TestAlexaDeviceId2',
                                 engine_schedule='TestEngineSchedule', )

        cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_3 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.playlist_2.add_audio_file(cls.audio_file_1)
        cls.playlist_2.add_audio_file(cls.audio_file_2)
        cls.play_list_has_audio_1.playlist.add_audio_file(cls.audio_file_3)
        u = Playlist.objects.all()[0]  # to make sure default playlist have no user assigned
        u.user_id = None
        u.save()

    def test_cold_start_next_command(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[1]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_playback_next_command = request_body_creator_for_next_command(True, token)
        data = stream_io(request_body_playback_next_command)

        expected_url = PlaylistHasAudio.objects.all()[3].audio.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']

        expected_next_token = str(
            PlaylistHasAudio.objects.all()[3].hash) + ',' + str(PlaylistHasAudio.objects.all()[3].audio_id)
        response_token = data['response']['directives'][0]['audioItem']['stream']['token']

        self.assertEqual(expected_url, response_url)
        self.assertEqual(expected_next_token, response_token)

    def test_user_playlist_next_command(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[0]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_playback_next_command = request_body_creator_for_next_command(False, token)
        data = stream_io(request_body_playback_next_command)

        expected_url = PlaylistHasAudio.objects.all()[2].audio.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']

        expected_next_token = str(
            PlaylistHasAudio.objects.all()[2].hash) + ',' + str(PlaylistHasAudio.objects.all()[2].audio_id)
        response_token = data['response']['directives'][0]['audioItem']['stream']['token']

        self.assertEqual(expected_url, response_url)
        self.assertEqual(expected_next_token, response_token)

    def test_cold_start_next_intent(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[1]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_playback_next_command = request_body_creator_for_intent(True, 'AMAZON.NextIntent')
        data = stream_io(request_body_playback_next_command)

        expected_url = PlaylistHasAudio.objects.all()[3].audio.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']

        expected_next_token = str(
            PlaylistHasAudio.objects.all()[3].hash) + ',' + str(PlaylistHasAudio.objects.all()[3].audio_id)
        response_token = data['response']['directives'][0]['audioItem']['stream']['token']

        self.assertEqual(expected_url, response_url)
        self.assertEqual(expected_next_token, response_token)

    def test_user_playlist_next_intent(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[0]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_playback_next_command = request_body_creator_for_intent(False, 'AMAZON.NextIntent')
        data = stream_io(request_body_playback_next_command)

        expected_url = PlaylistHasAudio.objects.all()[2].audio.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']

        expected_next_token = str(
            PlaylistHasAudio.objects.all()[2].hash) + ',' + str(PlaylistHasAudio.objects.all()[2].audio_id)
        response_token = data['response']['directives'][0]['audioItem']['stream']['token']

        self.assertEqual(expected_url, response_url)
        self.assertEqual(expected_next_token, response_token)

    def test_cold_start_nearly_finished_request(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[1]
        expected_previous_token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(True,
                                                                            'AudioPlayer.PlaybackStarted',
                                                                            expected_previous_token
                                                                            )
        stream_io(request_body_playback_start)

        request_body_playback_nearly_finished = \
            request_body_creator_for_audio_player(True,
                                                  'AudioPlayer.PlaybackNearlyFinished',
                                                  expected_previous_token
                                                  )
        data = stream_io(request_body_playback_nearly_finished)

        expected_url = PlaylistHasAudio.objects.all()[3].audio.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_next_token = str(
            PlaylistHasAudio.objects.all()[3].hash) + ',' + str(PlaylistHasAudio.objects.all()[3].audio_id)
        response_next_token = data['response']['directives'][0]['audioItem']['stream']['token']
        response_previous_token = data['response']['directives'][0]['audioItem']['stream']['expectedPreviousToken']

        self.assertEqual(expected_url, response_url)
        self.assertEqual(expected_next_token,  response_next_token)
        self.assertEqual(response_previous_token, expected_previous_token)

    def test_user_playlist_nearly_finished_request(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[0]
        expected_previous_token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = \
            request_body_creator_for_audio_player(False,
                                                  'AudioPlayer.PlaybackStarted',
                                                  expected_previous_token
                                                  )
        stream_io(request_body_playback_start)

        request_body_playback_nearly_finished = \
            request_body_creator_for_audio_player(False,
                                                  'AudioPlayer.PlaybackNearlyFinished',
                                                  expected_previous_token
                                                  )
        data = stream_io(request_body_playback_nearly_finished)

        expected_url = PlaylistHasAudio.objects.all()[2].audio.url
        response_url = data['response']['directives'][0]['audioItem']['stream']['url']
        expected_next_token = str(
            PlaylistHasAudio.objects.all()[2].hash) + ',' + str(PlaylistHasAudio.objects.all()[2].audio_id)
        response_next_token = data['response']['directives'][0]['audioItem']['stream']['token']
        response_previous_token = data['response']['directives'][0]['audioItem']['stream']['expectedPreviousToken']

        self.assertEqual(expected_url, response_url)
        self.assertEqual(expected_next_token, response_next_token)
        self.assertEqual(response_previous_token, expected_previous_token)


class StreamingPauseAndFillerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.play_list_has_audio_1 = mommy.make_recipe('streaming.playlist_has_audio_recipe')
        cls.playlist_2 = mommy.make_recipe('streaming.playlist_recipe_2')  # second time user2 recipe runs

        cls.auser_2 = mommy.make(AUser,
                                 user=cls.playlist_2.user,
                                 alexa_user_id='TestAlexaUserId2',
                                 alexa_device_id='TestAlexaDeviceId2',
                                 engine_schedule='TestEngineSchedule', )

        cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.audio_file_3 = mommy.make_recipe('streaming.audio_file_recipe')
        cls.playlist_2.add_audio_file(cls.audio_file_1)
        cls.playlist_2.add_audio_file(cls.audio_file_2)
        cls.play_list_has_audio_1.playlist.add_audio_file(cls.audio_file_3)
        u = Playlist.objects.all()[0]  # to make sure default playlist have no user assigned
        u.user_id = None
        u.save()

    def test_cold_start_pause_command(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[1]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_pause_command = request_body_creator_for_pause_command(True, token)
        data = stream_io(request_body_pause_command)

        response = data['response']['shouldEndSession']
        expected_ups_audio = PlaylistHasAudio.objects.all()[3].audio
        next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio

        self.assertTrue(response)
        self.assertEqual(next_ups_audio, expected_ups_audio)

    def test_user_playlist_pause_command(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[0]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_pause_command = request_body_creator_for_pause_command(False, token)
        data = stream_io(request_body_pause_command)

        response = data['response']['shouldEndSession']
        expected_ups_audio = PlaylistHasAudio.objects.all()[2].audio
        next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio

        self.assertTrue(response)
        self.assertEqual(next_ups_audio, expected_ups_audio)

    def test_cold_start_pause_intent(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[1]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_pause_command = request_body_creator_for_intent(True, 'AMAZON.PauseIntent')
        data = stream_io(request_body_pause_command)

        response = data['response']['shouldEndSession']
        expected_ups_audio = PlaylistHasAudio.objects.all()[3].audio
        next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio

        self.assertTrue(response)
        self.assertEqual(next_ups_audio, expected_ups_audio)

    def test_user_playlist_pause_intent(self):
        pha_object = type(self.play_list_has_audio_1).objects.all()[0]
        token = str(pha_object.hash) + ',' + str(pha_object.audio_id)

        request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
        stream_io(request_body_playback_start)

        request_body_pause_command = request_body_creator_for_intent(False, 'AMAZON.PauseIntent')
        data = stream_io(request_body_pause_command)

        response = data['response']['shouldEndSession']
        expected_ups_audio = PlaylistHasAudio.objects.all()[2].audio
        next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio

        self.assertTrue(response)
        self.assertEqual(next_ups_audio, expected_ups_audio)

    def test_none_intent(self):
        none_intent = request_body_creator_for_intent(False, 'None_Intent')
        data = stream_io(none_intent)
        is_session_ended = data['response']['shouldEndSession']
        audio_player_directive = data['response']['directives'][0]['type']

        self.assertTrue(is_session_ended)
        self.assertEqual(audio_player_directive, 'AudioPlayer.Stop')

    def test_fallback_filler(self):
        fallback_request = request_body_creator(False, 'fallback')
        data = stream_io(fallback_request)
        is_session_ended = data['response']['shouldEndSession']

        self.assertTrue(is_session_ended)
