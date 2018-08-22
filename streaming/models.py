from django.db import models
from model_utils.models import TimeStampedModel
from jsonfield import JSONField
from alexa.models import User
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


class AudioFile(TimeStampedModel):
    class Meta:
        db_table = 'audio_file'

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


AudioFile._meta.get_field('modified').db_index = True


def audio_file_accessibility_and_duration(sender, instance, raw, using, update_fields, **kwargs):
    try:
        filename, headers = urlretrieve(instance.url)
        audio = MP3(filename)
        instance.duration = round(audio.info.length)
    except HTTPError:
        instance.duration = -1


signals.pre_save.connect(receiver=audio_file_accessibility_and_duration,
                         sender=AudioFile)


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
                              on_delete=models.CASCADE, )
    order_id = models.FloatField(blank=False,
                                 null=False,
                                 db_index=True, )
    play_date = models.DateField(null=True,
                                 blank=True, )
    play_time = models.TextField(null=False,
                                 blank=False,
                                 choices=TIME_SET,
                                 default=TIME_DAYLONG)

    def time_based_filtered_content(self, daytime):
        now = datetime.utcnow()
        qs = self.playlist.playlisthasaudio_set.select_for_update() \
            .filter(order_id__gt=self.order_id) \
            .filter(Q(play_date__isnull=True) | Q(play_date=now.today()))\
            .filter(Q(play_time='daylong') | Q(play_time=daytime))
        return qs

    def next(self):
        now = datetime.utcnow()
        if 12 < now.hour <= 19:
            daytime = 'morning'
            qs = self.time_based_filtered_content(daytime)

        elif 19 < now.hour <= 23 or now.hour <= 1:
            daytime = 'afternoon'
            qs = self.time_based_filtered_content(daytime)
        elif 1 < now.hour < 6:
            daytime = 'evening'
            qs = self.time_based_filtered_content(daytime)
        else:
            daytime = 'night'
            qs = self.time_based_filtered_content(daytime)

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

    offset = models.IntegerField(default=0,
                                 help_text='The place user left the song in milliseconds', )

    @classmethod
    def get_users_playlist(cls, user: User):
        qs = user.playlist_set.all()
        return user.playlist_set.all()[0] if qs.count() >= 1 else Playlist.get_default()

    @classmethod
    def get_user_playlist_status_for_user(cls, user: User):
        obj_instance, created = cls.objects.select_for_update().get_or_create(
            user=user,
            defaults={
                'playlist_has_audio': cls.get_users_playlist(user).playlisthasaudio_set.all()[0],
            }
        )
        return obj_instance, created


class HardwareRegistry(TimeStampedModel):
    class Meta:
        db_table = 'hardware_registry'

    caressa_device_id = models.CharField(max_length=100, blank=False, null=False)   # e.g. CA-AMZ-001
    device_id = models.TextField()      # Alexa ID  todo: when Alexa User is changed on Alexa device is it updated?
    notes = models.TextField(default='')
