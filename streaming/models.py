from caressa.settings import AUTH_USER_MODEL as User
from django.db import models
from model_utils.models import TimeStampedModel
from jsonfield import JSONField
from django.db.models import signals
from urllib.request import urlretrieve
from mutagen.mp3 import MP3
from urllib.error import HTTPError
from django.utils.html import format_html
from django.db.models import Sum
from utilities.models.mixins import CacheMixin, CacheMiss
from utilities.time import seconds_to_minutes
from datetime import datetime
from django.db.models import Q
from random import randint
from uuid import uuid4


class Tag(TimeStampedModel):
    class Meta:
        db_table = 'tag'

    name = models.TextField(null=False,
                            blank=False, )
    label = models.TextField(null=False,
                             blank=False,
                             help_text=(
                                 "Label is the text that is readable by the users. Tags are exposed as settings "
                                 "for end user if `is_setting_available` set for the tag. An example for label is "
                                 "'Classical Music' for classical songs, where name may be 'song-classical'."
                             ), )
    is_setting_available = models.BooleanField(null=False,
                                               blank=False,
                                               help_text=(
                                                   "This makes the tag available as settings on the family mobile app."
                                               ), )

    @staticmethod
    def tag_list_to_audio_file(tag_list: list) -> ['AudioFile']:

        tag_list = list(map(int, tag_list))

        if len(tag_list) < 1:
            tag_list = Tag.default_tags_list()
        tags = Tag.objects.all().filter(pk__in=tag_list)
        qs = AudioFile.objects.all().filter(tags__in=tags)
        qs_count = qs.count()

        random_slice = randint(0, qs_count - 1)
        result_set = qs[random_slice: random_slice + 1]
        return result_set[0]

    @staticmethod
    def default_tags_list():
        tag_qs = Tag.objects.all().filter(is_setting_available=True)
        lst = []
        for tag in tag_qs:
            lst.append(tag.id)
        return lst


class AudioFile(TimeStampedModel):
    class Meta:
        db_table = 'audio_file'
        verbose_name_plural = 'Audio Files'

    TYPE_SONG = 'song'
    TYPE_PODCAST = 'podcast'
    TYPE_NEWS = 'news'
    TYPE_JOKE = 'joke'
    TYPE_FACT = 'fact'
    TYPE_FAMILY_UPDATE = 'family_update'
    TYPE_MISC = 'miscellaneous'

    TYPE_SET = (
        (TYPE_SONG, 'Song'),
        (TYPE_PODCAST, 'Podcast'),
        (TYPE_NEWS, 'News'),
        (TYPE_JOKE, 'Joke'),
        (TYPE_FACT, 'Fact'),
        (TYPE_FAMILY_UPDATE, 'Family Update'),
        (TYPE_MISC, 'Miscellaneous'),
    )

    audio_type = models.CharField(max_length=50,
                                  choices=TYPE_SET, )
    url = models.TextField(blank=False,
                           null=False,
                           db_index=True,
                           help_text='File URL, it must be publicly accessible', )
    duration = models.IntegerField(blank=False,
                                   null=False,
                                   default=0,
                                   help_text='Duration of content in seconds', )
    name = models.TextField(blank=False,
                            null=False,
                            db_index=True,
                            help_text='For internal use only', )

    tags = models.ManyToManyField(to=Tag)

    description = models.TextField(blank=True,
                                   null=False,
                                   default='',
                                   help_text='For Internal Use only', )
    payload = JSONField(default={})

    def __str__(self):
        return "({audio_type}) {file_name}".format(audio_type=self.audio_type, file_name=self.name)

    def url_hyperlink(self):
        return format_html("<a href='{url}' target='_blank'>{url}</a>".format(url=self.url))

    @property
    def duration_in_minutes(self):
        return seconds_to_minutes(self.duration)

    def is_publicly_accessible(self):
        return self.duration >= 0
    is_publicly_accessible.admin_order_field = 'duration'

    @property
    def tag_list(self):
        if self.tags.all().count() > 0:
            return [tag.name for tag in self.tags.all()]

        return []


AudioFile._meta.get_field('modified').db_index = True


def audio_file_accessibility_and_duration(sender, instance, raw, using, update_fields, **kwargs):
    try:
        filename, headers = urlretrieve(instance.url)
        audio = MP3(filename)
        instance.duration = round(audio.info.length)
    except HTTPError:
        instance.duration = -1


signals.pre_save.connect(receiver=audio_file_accessibility_and_duration,
                         sender=AudioFile, dispatch_uid='audio_file_accessibility_and_duration')


class Playlist(CacheMixin, TimeStampedModel):
    class Meta:
        db_table = 'playlist'
        ordering = ['id', ]

    DEFAULT_PLAYLIST_NAME = 'cold-start'

    user = models.ForeignKey(to=User,
                             null=True,
                             blank=True,
                             help_text='Who is it for?',
                             on_delete=models.DO_NOTHING, )
    name = models.TextField(blank=True,
                            null=False,
                            default='',
                            db_index=True,
                            help_text='Playlist name', )
    audio_files = models.ManyToManyField(to=AudioFile,
                                         through='PlaylistHasAudio', )

    def get_audio_files(self):
        return self.audio_files.order_by('playlisthasaudio')

    def add_audio_file(self, audio_file: AudioFile):
        if self.playlisthasaudio_set.count() < 1:
            pha = PlaylistHasAudio.objects.create(playlist=self,
                                                  audio=audio_file,
                                                  order_id=10)
            pha.save()
            return pha

        playlist_has_audio_last_one = self.playlisthasaudio_set.all().order_by('-order_id')[0]
        pha = PlaylistHasAudio.objects.create(playlist=self,
                                              audio=audio_file,
                                              order_id=playlist_has_audio_last_one.order_id + 10)
        pha.save()
        return pha

    def _compute_total_duration(self):
        total_duration = self.audio_files.aggregate(Sum('duration'))['duration__sum']
        return total_duration if total_duration else 0

    def _compute_number_of_audio(self):
        return self.audio_files.count()

    @property
    def total_duration(self):
        cache_key = 'total_duration'
        try:
            total_duration = self.get_cache_value(cache_key)
        except CacheMiss:
            total_duration = self._compute_total_duration()
            self.set_cache_value(cache_key, total_duration)
        return total_duration

    @property
    def number_of_audio(self):
        cache_key = 'audio_count'
        try:
            audio_count = self.get_cache_value(cache_key)
        except CacheMiss:
            audio_count = self._compute_number_of_audio()
            self.set_cache_value(cache_key, audio_count)
        return audio_count

    @classmethod
    def get_default(cls):
        qs = cls.objects.filter(name__iexact=cls.DEFAULT_PLAYLIST_NAME)
        if qs.count() < 1:
            raise Exception('No Default Playlist specified. Set the name of one playlist to: "{}"'.format(cls.name))
        return qs[0]

    def __str__(self):
        duration = seconds_to_minutes(self.total_duration)
        return "{name} (duration: {duration}, #files: {num_files})".format(name=self.name,
                                                                           duration=duration,
                                                                           num_files=self.number_of_audio, )


class PlaylistHasAudio(TimeStampedModel):
    class Meta:
        db_table = 'playlist_has_audio'
        ordering = ['order_id', ]
        verbose_name_plural = 'Playlist Has Audios'

    TIME_MORNING = 'morning'
    TIME_AFTERNOON = 'afternoon'
    TIME_EVENING = 'evening'
    TIME_NIGHT = 'night'
    TIME_DAYLONG = 'daylong'

    TIME_SET = (
        (TIME_MORNING, 'Morning'),
        (TIME_AFTERNOON, 'Afternoon'),
        (TIME_EVENING, 'Evening'),
        (TIME_NIGHT, 'Night'),
        (TIME_DAYLONG, 'Daylong'),
    )

    playlist = models.ForeignKey(to=Playlist,
                                 on_delete=models.DO_NOTHING, )
    audio = models.ForeignKey(to=AudioFile,
                              on_delete=models.CASCADE,
                              default=None,
                              null=True, )

    # tag: string combination of tags, e.g. "song-classical, update-{date}"
    tag = models.TextField(blank=True,
                           default='',
                           help_text='If there is an audio file specified in "Audio" section, these tags are going to '
                                     'be ignored!', )

    order_id = models.FloatField(blank=False,
                                 null=False,
                                 db_index=True, )
    play_date = models.DateField(null=True,
                                 blank=True, )
    play_time = models.TextField(null=False,
                                 blank=False,
                                 choices=TIME_SET,
                                 default=TIME_DAYLONG, )

    hash = models.UUIDField(default=uuid4)

    def _current_daytime(self):
        now = datetime.utcnow()
        if 12 < now.hour <= 19:
            return self.TIME_MORNING
        elif 19 < now.hour <= 23 or now.hour <= 1:
            return self.TIME_AFTERNOON
        elif 1 < now.hour < 6:
            return self.TIME_EVENING
        else:
            return self.TIME_NIGHT

    def _time_based_filter(self, daytime):
        now = datetime.utcnow()
        qs = self.playlist.playlisthasaudio_set.select_for_update()

        return qs.filter(Q(play_date__isnull=True) | Q(play_date=now.today()))\
            .filter(Q(play_time=self.TIME_DAYLONG) | Q(play_time=daytime))

    def time_based_filtered_content(self, daytime):
        return self._time_based_filter(daytime).filter(order_id__gt=self.order_id)

    def current_content_time_filter(self, daytime):
        return self._time_based_filter(daytime).filter(order_id=self.order_id)

    def is_current_content_time_fit(self):
        current_daytime = self._current_daytime()
        qs = self.current_content_time_filter(current_daytime)
        return qs.count() >= 1

    def next(self):
        current_daytime = self._current_daytime()
        qs = self.time_based_filtered_content(current_daytime)
        if qs.count() < 1:
            return self.playlist.playlisthasaudio_set.all()[0]
        return qs[0]


def invalidate_playlist_caches(sender, instance, *args, **kwargs):
    if instance:    # type: PlaylistHasAudio
        instance.playlist.invalidate_cache()

    if instance.id:
        old_entry = PlaylistHasAudio.objects.get(pk=instance.id)
        old_entry.playlist.invalidate_cache()


signals.pre_save.connect(receiver=invalidate_playlist_caches,
                         sender=PlaylistHasAudio)

signals.pre_delete.connect(receiver=invalidate_playlist_caches,
                           sender=PlaylistHasAudio)


class UserPlaylistStatus(TimeStampedModel):
    class Meta:
        db_table = 'user_playlist_status'
        ordering = ['id', ]

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING, )

    # todo think about deletion with user progress case
    playlist_has_audio = models.ForeignKey(to=PlaylistHasAudio,
                                           on_delete=models.DO_NOTHING, )
    current_active_audio = models.ForeignKey(to=AudioFile,
                                             on_delete=models.DO_NOTHING,
                                             null=True, )

    offset = models.IntegerField(default=0,
                                 help_text='The place user left the song in milliseconds', )

    @classmethod
    def get_users_playlist(cls, user: User):
        qs = user.playlist_set.all()
        return user.playlist_set.all()[0] if qs.count() >= 1 else Playlist.get_default()

    @classmethod
    def get_user_playlist_status_for_user(cls, user: User): # todo not in use. delete?
        playlist_entries_qs = cls.get_users_playlist(user).playlisthasaudio_set.all()

        obj_instance, created = cls.objects.select_for_update().get_or_create(
            user=user,
            defaults={
                'playlist_has_audio': playlist_entries_qs[0],
                'current_active_audio': user.get_audio,
            }
        )
        return obj_instance, created


class UserAudioStatus(TimeStampedModel):
    class Meta:
        db_table = 'user_audio_status'
        ordering = ['id', ]

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING, )

    current_active_audio = models.ForeignKey(to=AudioFile,
                                             on_delete=models.DO_NOTHING,
                                             null=True, )

    @classmethod
    def get_user_audio_status_for_user(cls, user: User):
        obj_instance, created = cls.objects.select_for_update().get_or_create(
            user=user,
            defaults={
                'current_active_audio': user.get_audio,
            }
        )
        return obj_instance, created


class Messages(TimeStampedModel):
    class Meta:
        db_table = 'message_queue'

    PROCESS_QUEUED = 'queued'
    PROCESS_COMPLETE = 'complete'
    PROCESS_FAILED = 'failed'
    PROCESS_RUNNING = 'running'

    PROCESS_SET = (
        (PROCESS_QUEUED, 'Queued'),
        (PROCESS_COMPLETE, 'Complete'),
        (PROCESS_FAILED, 'Failed'),
        (PROCESS_RUNNING, 'Running'),
    )

    message = JSONField(default={})

    process_state = models.CharField(max_length=50,
                                     choices=PROCESS_SET,
                                     default=PROCESS_QUEUED,
                                     db_index=True, )

Messages._meta.get_field('created').db_index = True


class VoiceMessageStatus(TimeStampedModel):
    class Meta:
        db_table = 'voice_message_status'

    VOICE_STATUS_LISTENED = 'listened'
    VOICE_STATUS_WAITING = 'waiting'

    VOICE_STATUS_SET = (
        (VOICE_STATUS_LISTENED, 'Listened'),
        (VOICE_STATUS_WAITING, 'Waiting')
    )
    source = models.ForeignKey(to=User,
                               null=False,
                               help_text='Voice Source User',
                               on_delete=models.DO_NOTHING,
                               related_name='voice_source_user'
                               )
    destination = models.ForeignKey(to=User,
                                    null=True,
                                    help_text='Voice Destination User (None means facility-wide message)',
                                    on_delete=models.DO_NOTHING,
                                    related_name='voice_destination_user'
                                    )
    key = models.TextField(null=False,
                           help_text='File name that will be listened by destination', )
    list_status = models.CharField(max_length=50,
                                   choices=VOICE_STATUS_SET,
                                   default=VOICE_STATUS_WAITING,
                                   )
