from django.test import TestCase
from model_mommy import mommy
from streaming.models import Tag, AudioFile, audio_file_accessibility_and_duration, Playlist, PlaylistHasAudio
from django.db.models import signals


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

    def test_is_publicly_accessible(self):  # todo how to?
        pass

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
        self.assertRaises(Exception, lambda: Playlist.get_default())

        Playlist.DEFAULT_PLAYLIST_NAME = 'playlist'
        fetched_default_name = Playlist.get_default()
        expected_default_name = Playlist.objects.all()[0]

        self.assertEqual(fetched_default_name, expected_default_name)

    def test_string_representation(self):
        fetched_string_representation = str(Playlist.objects.all()[0])
        expected_string_representation = "{name} (duration: {duration}," \
                                         " #files: {num_files})".format(name='playlist',
                                                                        duration='13 sec(s)',
                                                                        num_files=1, )

        self.assertEqual(fetched_string_representation, expected_string_representation)
#
# class PlaylistHasAudioModelTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass
#
#     def test_hash_creation(self):
#         # two instances are expected to have different hash values
#         pass
#
#     def test_get_audio_with_static_audio_only(self):
#         pass
#
#     def test_get_audio_with_static_audio_and_tag(self):
#         pass
#
#     def test_get_audio_with_tag_only(self):
#         pass
#
#     def test_next_no_date_no_time(self):
#         pass
#
#     def test_next_only_date_no_time(self):
#         pass
#
#     def test_next_no_date_only_time(self):
#         pass
#
#     def test_next_date_and_time(self):
#         pass
#
#
# class UserPlaylistStatusModelTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass
#
#     def test_ordering(self):
#         pass
#
#     def test_get_users_playlist(self):
#         pass
#
#     def get_user_playlist_status_for_user(self):
#         pass
#
#
# class TrackingActionModelTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass
#
#     def save_action_partial_segments(self):
#         # test giving only `segment1`
#         pass
#
#     def save_action_full_segments(self):
#         # test giving all segments
#         pass
#
#
# class StreamingPlayTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass
#
#     def test_cold_start_launch_request(self):
#         pass
#
#     def test_user_playlist_launch_request(self):
#         pass
#
#     def test_cold_start_play_command(self):
#         pass
#
#     def test_user_playlist_play_command(self):
#         pass
#
#     def test_cold_start_resume_intent(self):
#         pass
#
#     def test_user_playlist_resume_intent(self):
#         pass
#
#     def test_cold_start_playback_started_request(self):
#         pass
#
#     def test_user_playlist_playback_started_request(self):
#         pass
#
#
# class StreamingNextAndQueueTestCase(TestCase):
#     def test_cold_start_next_command(self):
#         pass
#
#     def test_user_playlist_next_command(self):
#         pass
#
#     def test_cold_start_next_intent(self):
#         pass
#
#     def test_user_playlist_next_intent(self):
#         pass
#
#     def test_cold_start_nearly_finished_request(self):
#         pass
#
#     def test_user_playlist_nearly_finished_request(self):
#         pass
#
#
# class StreamingPauseAndFillerTestCase(TestCase):
#     def test_cold_start_pause_command(self):
#         pass
#
#     def test_user_playlist_pause_command(self):
#         pass
#
#     def test_cold_start_pause_intent(self):
#         pass
#
#     def test_user_playlist_pause_intent(self):
#         pass
#
#     def test_none_intent(self):
#         pass
#
#     def test_fallback_filler(self):
#         pass
