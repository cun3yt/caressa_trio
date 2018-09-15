from django.test import TestCase
from model_mommy import mommy
from streaming.models import Tag, AudioFile


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
        pass

    def test_url_hyperlink(self):
        pass

    def test_duration_in_minutes(self):
        pass

    def test_is_publicly_accessible(self):
        pass

    def test_string_representation(self):
        pass


# class PlaylistModelTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         pass
#
#     def test_getting_audio_files(self):
#         pass
#
#     def test_adding_audio_file(self):
#         pass
#
#     def test_total_duration(self):
#         pass
#
#     def test_number_of_audio(self):
#         pass
#
#     def test_get_default(self):
#         pass
#
#     def test_string_representation(self):
#         pass
#
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
