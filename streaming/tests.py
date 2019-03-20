from django.test import TestCase
from mock import patch
from model_mommy import mommy
from streaming.models import Tag, AudioFile, audio_file_accessibility_and_duration
# from streaming.views import stream_io
from django.db.models import signals
import datetime
import boto3
from random import randint
# from streaming.test_helper_functions import request_body_creator_for_next_command, request_body_creator_for_intent, \
#     request_body_creator, request_body_creator_for_audio_player, request_body_creator_for_pause_command
# import botocore


class TagModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        signals.pre_save.disconnect(receiver=audio_file_accessibility_and_duration,
                                    sender=AudioFile, dispatch_uid='audio_file_accessibility_and_duration')

        tag1 = mommy.make(Tag, name='song-classical')
        cls.user_one = mommy.make_recipe('alexa.user')
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

    # def test_tag_string_to_audio_file(self):
    #     tag_id = '2'
    #     audio_file_fetched = Tag.string_to_audio_file(tag_id)
    #     self.assertEqual(audio_file_fetched, self.audio_file1)
    #
    #     tag_id2 = '2, 3, 4'
    #     audio_file_fetched = Tag.string_to_audio_file(tag_id2)
    #     self.assertEqual(audio_file_fetched, self.audio_file1)
    #
    #     tag_id3 = '2, 3, 4'
    #     audio_file_fetched = Tag.string_to_audio_file(tag_id3)
    #     self.assertEqual(audio_file_fetched, self.audio_file1)
    #
    # def test_tag_string_to_not_none(self):
    #     tag_str =
    #     audio_file_fetched = Tag.string_to_audio_file(tag_str)
    #     self.assertIsNotNone(audio_file_fetched, 'If no matching tag in audio files it leads to None')
    #
    # def test_tag_string_to_audio_with_multiple_tag(self):
    #     audio_file_fetched = Tag.string_to_audio_file('2')
    #     self.assertEqual(audio_file_fetched, self.audio_file_multi_tagged)
    #
    #     audio_file_fetched2 = Tag.string_to_audio_file('2, 2, 3, 4, 5')
    #     self.assertEqual(audio_file_fetched2, self.audio_file_multi_tagged)
    #
    #     audio_file_fetched3 = Tag.string_to_audio_file('5, 4, 3, 2')
    #     self.assertEqual(audio_file_fetched3, self.audio_file_multi_tagged)
    #
    #     audio_file_fetched4 = Tag.string_to_audio_file('3, 2, 4, 5, 6, 7')
    #     self.assertEqual(audio_file_fetched4, self.audio_file_multi_tagged)
    #
    #     audio_file_fetched5 = Tag.string_to_audio_file('3, 2')
    #     self.assertEqual(audio_file_fetched5, self.audio_file_multi_tagged)
    #
    #     audio_file_fetched6 = Tag.string_to_audio_file('2, 3, 4')
    #     self.assertIsNone(audio_file_fetched6)

    # def test_same_tag_multi_audio(self):
    #
    #     audio_file_fetched = Tag.string_to_audio_file('6')
    #     self.assertIn(audio_file_fetched, [self.same_tag_audio_file1, self.same_tag_audio_file2])
    #
    #     audio_file_fetched2 = Tag.string_to_audio_file('3')
    #     self.assertEqual(audio_file_fetched2, self.same_tag_audio_file1)


class AudioFileModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        signals.pre_save.disconnect(receiver=audio_file_accessibility_and_duration,
                                    sender=AudioFile, dispatch_uid='audio_file_accessibility_and_duration')
        cls.audio_file1 = mommy.make_recipe('streaming.audio_file_recipe', duration=40,
                                            name='song name')  # type: AudioFile
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
        self.assertEqual(actual_string_representation, "(song) song name")

# todo Read and enable tests: https://www.django-rest-framework.org/api-guide/testing/
#
# class StreamingPlayTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.play_list_has_audio_1 = mommy.make_recipe('streaming.playlist_has_audio_recipe')
#         cls.playlist_2 = mommy.make_recipe('streaming.playlist_recipe_2')   # second time user2 recipe runs
#
#         cls.auser_2 = mommy.make(AUser,
#                                  user=cls.playlist_2.user,
#                                  alexa_user_id='TestAlexaUserId2',
#                                  alexa_device_id='TestAlexaDeviceId2',
#                                  engine_schedule='TestEngineSchedule', )
#
#         cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.audio_file_3 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.playlist_2.add_audio_file(cls.audio_file_1)
#         cls.playlist_2.add_audio_file(cls.audio_file_2)
#         cls.play_list_has_audio_1.playlist.add_audio_file(cls.audio_file_3)
#         u = Playlist.objects.all()[0]  # to make sure default playlist have no user assigned
#         u.user_id = None
#         u.save()
#
#     def test_cold_start_launch_request(self):
#         request_body = request_body_creator(True, 'LaunchRequest')
#         data = stream_io(request_body)
#         response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_url_from_db = AudioFile.objects.all()[0].url
#         playlist_count = Playlist.objects.all().count()
#
#         self.assertIsNone(Playlist.objects.all()[0].user_id)
#         self.assertEqual(response_audio_url, expected_url_from_db)
#         self.assertEqual(playlist_count, 2)
#
#     def test_user_playlist_launch_request(self):
#         request_body = request_body_creator(False, 'LaunchRequest')
#         data = stream_io(request_body)
#         response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_url_from_db = AudioFile.objects.all()[1].url
#         playlist_count = Playlist.objects.all().count()
#
#         self.assertIsNotNone(Playlist.objects.all()[1].user_id)
#         self.assertEqual(response_audio_url, expected_url_from_db)
#         self.assertEqual(playlist_count, 2)
#
#     def test_cold_start_play_command(self):
#         request_body = request_body_creator(True, 'PlaybackController.PlayCommandIssued')
#         data = stream_io(request_body)
#         response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_url_from_db = AudioFile.objects.all()[0].url
#         playlist_count = Playlist.objects.all().count()
#
#         self.assertIsNone(Playlist.objects.all()[0].user_id)
#         self.assertEqual(response_audio_url, expected_url_from_db)
#         self.assertEqual(playlist_count, 2)
#
#     def test_user_playlist_play_command(self):
#         request_body = request_body_creator(False, 'PlaybackController.PlayCommandIssued')
#         data = stream_io(request_body)
#         response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_url_from_db = AudioFile.objects.all()[1].url
#         playlist_count = Playlist.objects.all().count()
#
#         self.assertIsNotNone(Playlist.objects.all()[1].user_id)
#         self.assertEqual(response_audio_url, expected_url_from_db)
#         self.assertEqual(playlist_count, 2)
#
#     def test_cold_start_resume_intent(self):
#         request_body = request_body_creator_for_intent(True, 'AMAZON.ResumeIntent')
#         data = stream_io(request_body)
#         response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_url_from_db = AudioFile.objects.all()[0].url
#         playlist_count = Playlist.objects.all().count()
#         self.assertIsNone(Playlist.objects.all()[0].user_id)
#         self.assertEqual(response_audio_url, expected_url_from_db)
#         self.assertEqual(playlist_count, 2)
#
#     def test_user_playlist_resume_intent(self):
#         request_body = request_body_creator_for_intent(False, 'AMAZON.ResumeIntent')
#         data = stream_io(request_body)
#         response_audio_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_url_from_db = AudioFile.objects.all()[1].url
#         playlist_count = Playlist.objects.all().count()
#
#         self.assertIsNotNone(Playlist.objects.all()[1].user_id)
#         self.assertEqual(response_audio_url, expected_url_from_db)
#         self.assertEqual(playlist_count, 2)
#
#     def test_cold_start_playback_started_request(self):
#
#         ups_count_before_save_state = UserPlaylistStatus.objects.all().count()
#         self.assertEqual(ups_count_before_save_state, 0)
#
#         pha_object = type(self.play_list_has_audio_1).objects.all()[1]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
#         data = stream_io(request_body)
#
#         response = data['response']['shouldEndSession']
#         ups_current_active_audio = UserPlaylistStatus.objects.all()[0].current_active_audio_id
#         ups_count_after_save_state = UserPlaylistStatus.objects.all().count()
#
#         self.assertEqual(ups_current_active_audio, pha_object.audio_id)
#         self.assertEqual(ups_count_after_save_state, 1)
#         self.assertTrue(response)
#
#     def test_user_playlist_playback_started_request(self):
#         ups_count_before_save_state = UserPlaylistStatus.objects.all().count()
#         self.assertEqual(ups_count_before_save_state, 0)
#
#         pha_object = type(self.play_list_has_audio_1).objects.all()[0]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
#         data = stream_io(request_body)
#
#         response = data['response']['shouldEndSession']
#         ups_current_active_audio = UserPlaylistStatus.objects.all()[0].current_active_audio_id
#         ups_count_after_save_state = UserPlaylistStatus.objects.all().count()
#
#         self.assertEqual(ups_current_active_audio, pha_object.audio_id)
#         self.assertEqual(ups_count_after_save_state, 1)
#         self.assertTrue(response)
#
#
# class StreamingNextAndQueueTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.play_list_has_audio_1 = mommy.make_recipe('streaming.playlist_has_audio_recipe')
#         cls.playlist_2 = mommy.make_recipe('streaming.playlist_recipe_2')  # second time user2 recipe runs
#
#         cls.auser_2 = mommy.make(AUser,
#                                  user=cls.playlist_2.user,
#                                  alexa_user_id='TestAlexaUserId2',
#                                  alexa_device_id='TestAlexaDeviceId2',
#                                  engine_schedule='TestEngineSchedule', )
#
#         cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.audio_file_3 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.playlist_2.add_audio_file(cls.audio_file_1)
#         cls.playlist_2.add_audio_file(cls.audio_file_2)
#         cls.play_list_has_audio_1.playlist.add_audio_file(cls.audio_file_3)
#         u = Playlist.objects.all()[0]  # to make sure default playlist have no user assigned
#         u.user_id = None
#         u.save()
#
#     def test_cold_start_next_command(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[1]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_playback_next_command = request_body_creator_for_next_command(True, token)
#         data = stream_io(request_body_playback_next_command)
#
#         expected_url = PlaylistHasAudio.objects.all()[3].audio.url
#         response_url = data['response']['directives'][0]['audioItem']['stream']['url']
#
#         expected_next_token = str(
#             PlaylistHasAudio.objects.all()[3].hash) + ',' + str(PlaylistHasAudio.objects.all()[3].audio_id)
#         response_token = data['response']['directives'][0]['audioItem']['stream']['token']
#
#         self.assertEqual(expected_url, response_url)
#         self.assertEqual(expected_next_token, response_token)
#
#     def test_user_playlist_next_command(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[0]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_playback_next_command = request_body_creator_for_next_command(False, token)
#         data = stream_io(request_body_playback_next_command)
#
#         expected_url = PlaylistHasAudio.objects.all()[2].audio.url
#         response_url = data['response']['directives'][0]['audioItem']['stream']['url']
#
#         expected_next_token = str(
#             PlaylistHasAudio.objects.all()[2].hash) + ',' + str(PlaylistHasAudio.objects.all()[2].audio_id)
#         response_token = data['response']['directives'][0]['audioItem']['stream']['token']
#
#         self.assertEqual(expected_url, response_url)
#         self.assertEqual(expected_next_token, response_token)
#
#     def test_cold_start_next_intent(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[1]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_playback_next_command = request_body_creator_for_intent(True, 'AMAZON.NextIntent')
#         data = stream_io(request_body_playback_next_command)
#
#         expected_url = PlaylistHasAudio.objects.all()[3].audio.url
#         response_url = data['response']['directives'][0]['audioItem']['stream']['url']
#
#         expected_next_token = str(
#             PlaylistHasAudio.objects.all()[3].hash) + ',' + str(PlaylistHasAudio.objects.all()[3].audio_id)
#         response_token = data['response']['directives'][0]['audioItem']['stream']['token']
#
#         self.assertEqual(expected_url, response_url)
#         self.assertEqual(expected_next_token, response_token)
#
#     def test_user_playlist_next_intent(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[0]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_playback_next_command = request_body_creator_for_intent(False, 'AMAZON.NextIntent')
#         data = stream_io(request_body_playback_next_command)
#
#         expected_url = PlaylistHasAudio.objects.all()[2].audio.url
#         response_url = data['response']['directives'][0]['audioItem']['stream']['url']
#
#         expected_next_token = str(
#             PlaylistHasAudio.objects.all()[2].hash) + ',' + str(PlaylistHasAudio.objects.all()[2].audio_id)
#         response_token = data['response']['directives'][0]['audioItem']['stream']['token']
#
#         self.assertEqual(expected_url, response_url)
#         self.assertEqual(expected_next_token, response_token)
#
#     def test_cold_start_nearly_finished_request(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[1]
#         expected_previous_token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(True,
#                                                                             'AudioPlayer.PlaybackStarted',
#                                                                             expected_previous_token
#                                                                             )
#         stream_io(request_body_playback_start)
#
#         request_body_playback_nearly_finished = \
#             request_body_creator_for_audio_player(True,
#                                                   'AudioPlayer.PlaybackNearlyFinished',
#                                                   expected_previous_token
#                                                   )
#         data = stream_io(request_body_playback_nearly_finished)
#
#         expected_url = PlaylistHasAudio.objects.all()[3].audio.url
#         response_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_next_token = str(
#             PlaylistHasAudio.objects.all()[3].hash) + ',' + str(PlaylistHasAudio.objects.all()[3].audio_id)
#         response_next_token = data['response']['directives'][0]['audioItem']['stream']['token']
#         response_previous_token = data['response']['directives'][0]['audioItem']['stream']['expectedPreviousToken']
#
#         self.assertEqual(expected_url, response_url)
#         self.assertEqual(expected_next_token,  response_next_token)
#         self.assertEqual(response_previous_token, expected_previous_token)
#
#     def test_user_playlist_nearly_finished_request(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[0]
#         expected_previous_token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = \
#             request_body_creator_for_audio_player(False,
#                                                   'AudioPlayer.PlaybackStarted',
#                                                   expected_previous_token
#                                                   )
#         stream_io(request_body_playback_start)
#
#         request_body_playback_nearly_finished = \
#             request_body_creator_for_audio_player(False,
#                                                   'AudioPlayer.PlaybackNearlyFinished',
#                                                   expected_previous_token
#                                                   )
#         data = stream_io(request_body_playback_nearly_finished)
#
#         expected_url = PlaylistHasAudio.objects.all()[2].audio.url
#         response_url = data['response']['directives'][0]['audioItem']['stream']['url']
#         expected_next_token = str(
#             PlaylistHasAudio.objects.all()[2].hash) + ',' + str(PlaylistHasAudio.objects.all()[2].audio_id)
#         response_next_token = data['response']['directives'][0]['audioItem']['stream']['token']
#         response_previous_token = data['response']['directives'][0]['audioItem']['stream']['expectedPreviousToken']
#
#         self.assertEqual(expected_url, response_url)
#         self.assertEqual(expected_next_token, response_next_token)
#         self.assertEqual(response_previous_token, expected_previous_token)
#
#
# class StreamingPauseAndFillerTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.play_list_has_audio_1 = mommy.make_recipe('streaming.playlist_has_audio_recipe')
#         cls.playlist_2 = mommy.make_recipe('streaming.playlist_recipe_2')  # second time user2 recipe runs
#
#         cls.auser_2 = mommy.make(AUser,
#                                  user=cls.playlist_2.user,
#                                  alexa_user_id='TestAlexaUserId2',
#                                  alexa_device_id='TestAlexaDeviceId2',
#                                  engine_schedule='TestEngineSchedule', )
#
#         cls.audio_file_1 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.audio_file_2 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.audio_file_3 = mommy.make_recipe('streaming.audio_file_recipe')
#         cls.playlist_2.add_audio_file(cls.audio_file_1)
#         cls.playlist_2.add_audio_file(cls.audio_file_2)
#         cls.play_list_has_audio_1.playlist.add_audio_file(cls.audio_file_3)
#         u = Playlist.objects.all()[0]  # to make sure default playlist have no user assigned
#         u.user_id = None
#         u.save()
#
#     def test_cold_start_pause_command(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[1]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_pause_command = request_body_creator_for_pause_command(True, token)
#         data = stream_io(request_body_pause_command)
#
#         response = data['response']['shouldEndSession']
#         expected_ups_audio = PlaylistHasAudio.objects.all()[3].audio
#         next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio
#
#         self.assertTrue(response)
#         self.assertEqual(next_ups_audio, expected_ups_audio)
#
#     def test_user_playlist_pause_command(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[0]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_pause_command = request_body_creator_for_pause_command(False, token)
#         data = stream_io(request_body_pause_command)
#
#         response = data['response']['shouldEndSession']
#         expected_ups_audio = PlaylistHasAudio.objects.all()[2].audio
#         next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio
#
#         self.assertTrue(response)
#         self.assertEqual(next_ups_audio, expected_ups_audio)
#
#     def test_cold_start_pause_intent(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[1]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(True, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_pause_command = request_body_creator_for_intent(True, 'AMAZON.PauseIntent')
#         data = stream_io(request_body_pause_command)
#
#         response = data['response']['shouldEndSession']
#         expected_ups_audio = PlaylistHasAudio.objects.all()[3].audio
#         next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio
#
#         self.assertTrue(response)
#         self.assertEqual(next_ups_audio, expected_ups_audio)
#
#     def test_user_playlist_pause_intent(self):
#         pha_object = type(self.play_list_has_audio_1).objects.all()[0]
#         token = str(pha_object.hash) + ',' + str(pha_object.audio_id)
#
#         request_body_playback_start = request_body_creator_for_audio_player(False, 'AudioPlayer.PlaybackStarted', token)
#         stream_io(request_body_playback_start)
#
#         request_body_pause_command = request_body_creator_for_intent(False, 'AMAZON.PauseIntent')
#         data = stream_io(request_body_pause_command)
#
#         response = data['response']['shouldEndSession']
#         expected_ups_audio = PlaylistHasAudio.objects.all()[2].audio
#         next_ups_audio = UserPlaylistStatus.objects.all()[0].current_active_audio
#
#         self.assertTrue(response)
#         self.assertEqual(next_ups_audio, expected_ups_audio)
#
#     def test_none_intent(self):
#         none_intent = request_body_creator_for_intent(False, 'None_Intent')
#         data = stream_io(none_intent)
#         is_session_ended = data['response']['shouldEndSession']
#         audio_player_directive = data['response']['directives'][0]['type']
#
#         self.assertTrue(is_session_ended)
#         self.assertEqual(audio_player_directive, 'AudioPlayer.Stop')
#
#     def test_fallback_filler(self):
#         fallback_request = request_body_creator(False, 'fallback')
#         data = stream_io(fallback_request)
#         is_session_ended = data['response']['shouldEndSession']
#
#         self.assertTrue(is_session_ended)
