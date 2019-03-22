from alexa import models as alexa_models
from caressa.settings import AUTH_USER_MODEL as User
from django.db import models
from model_utils.models import TimeStampedModel
from jsonfield import JSONField
from django.db.models import signals
from urllib.request import urlretrieve
from mutagen.mp3 import MP3
from urllib.error import HTTPError
from django.utils.html import format_html
from utilities.models.abstract_models import CreatedTimeStampedModel
from utilities.models.mixins import CacheMixin
from utilities.time import seconds_to_minutes
from random import randint


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
    def tag_list_to_audio_file(tag_list: list) -> 'AudioFile':
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
        return list(Tag.objects.all().filter(is_setting_available=True).values_list('id', flat=True))


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
        return list(self.tags.all().values_list('name', flat=True))

    @staticmethod
    def get_main_content_to_play(user):
        assert user.user_type == alexa_models.User.CARETAKER, (
            "Main Content Audio Play is only available for user_type: senior. "
            "It is {user_type} for user.id: {user_id}".format(user_type=user.user_type,
                                                              user_id=user.id)
        )

        user_settings, _ = alexa_models.UserSettings.objects.get_or_create(user=user)
        user_genres_id_list = user_settings.genres
        if len(user_genres_id_list) == 0:
            user_genres_id_list = Tag.default_tags_list()

        return Tag.tag_list_to_audio_file(user_genres_id_list)


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


class UserMainContentConsumption(CreatedTimeStampedModel):
    class Meta:
        db_table = 'user_audio_consumption'
        ordering = ['id', ]

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING, )

    played_main_content = models.ForeignKey(to=AudioFile,
                                            on_delete=models.DO_NOTHING,
                                            null=True, )


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
