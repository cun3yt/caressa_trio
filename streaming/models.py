from random import randint

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import signals
from django.utils.html import format_html

from alexa import models as alexa_models
from caressa.settings import AUTH_USER_MODEL as User
from model_utils.models import TimeStampedModel
from jsonfield import JSONField
from urllib.request import urlretrieve
from mutagen.mp3 import MP3
from urllib.error import HTTPError

from utilities.cryptography import compute_hash
from utilities.models.abstract_models import CreatedTimeStampedModel
from utilities.time import seconds_to_minutes


class Tag(TimeStampedModel):
    class Meta:
        db_table = 'tag'

    name = models.TextField(null=False,
                            blank=False,
                            help_text= (
                                "Name is how server use the tags. This is used for backend processes. "
                                "Use '-' (dash) instead of spaces and all lower case. E.g. 'song-jazz'"
                            ), )
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

    def __str__(self):
        return self.name


class AudioFile(TimeStampedModel):
    """
    Purpose: Keep an entry for all audio (mp3) files.
    """
    class Meta:
        db_table = 'audio_file'
        verbose_name_plural = 'Audio Files'

    TYPE_SONG = 'song'
    TYPE_FACILITY_AUTO_GENERATED_CONTENT = 'facility-auto-generated-content'
    TYPE_FAMILY_UPDATE = 'family_update'
    TYPE_MISC = 'miscellaneous'

    TYPE_SET = (
        (TYPE_SONG, 'Song'),
        (TYPE_FACILITY_AUTO_GENERATED_CONTENT, 'Facility Auto Generated Content'),
        (TYPE_FAMILY_UPDATE, 'Family Update'),
        (TYPE_MISC, 'Miscellaneous'),
    )

    audio_type = models.CharField(max_length=50,
                                  choices=TYPE_SET, )
    url = models.URLField(blank=False,
                          null=False,
                          db_index=True,
                          verbose_name='File URL',
                          help_text='File URL, it must be publicly accessible', )

    # duration is set by pre-save signal below
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

    hash = models.TextField(null=False,
                            blank=True,
                            default='',
                            db_index=True, )

    def __init__(self, *args, **kwargs):
        """
        If there is a `type` class variable in any subclass of `AudioFile` it will be treated as setting
        `audio_type` field's default value. For example in Song model, `audio_type`'s default is set to
        `AudioFile.TYPE_SONG` with the help of this initializer and the class variable `type`.
        """
        if hasattr(self, 'type'):
            self._meta.get_field('audio_type').default = self.type

            kwargs_type = kwargs.get('audio_type', None)
            if not kwargs_type:
                kwargs['audio_type'] = self.type

        super().__init__(*args, **kwargs)

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

    def _set_hash_if_not_set(self):
        """
        The hash may be set by the AudioFile's referer while creating it.
        Example: SeniorLivingFacilityContent sets the hash according to its own logic.

        :author Cuneyt Mertayak
        """

        if self.hash:
            return

        txt = "{}-{}".format(self.audio_type, self.url)
        self.hash = compute_hash(txt)

    def _set_duration(self):
        try:
            filename, headers = urlretrieve(self.url)
            audio = MP3(filename)
            self.duration = round(audio.info.length)
        except HTTPError:
            self.duration = -1

    @staticmethod
    def pre_save_operations(**kwargs):
        instance = kwargs.get('instance')   # type: 'AudioFile'
        instance._set_duration()
        instance._set_hash_if_not_set()

    def add_to_positive_negative_signal_by(self, user: User, signal_type='signal-positive'):
        return UserAudioFileSignal.objects.create(audio_file=self, user=user, signal=signal_type)


AudioFile._meta.get_field('modified').db_index = True


class Song(AudioFile):
    """
    This is a proxy model, just setting `type` to AudioFile.TYPE_SONG
    """
    class Meta:
        proxy = True

    class _Manager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(audio_type=AudioFile.TYPE_SONG)

    type = AudioFile.TYPE_SONG
    objects = _Manager()


audio_file_pre_save_signals = [
    {'sender': AudioFile,
     'uid': 'audio_file.pre_save', },
    {'sender': Song,
     'uid': 'song.pre_save', },
]

# All models (including proxy models) need their own signal-function connection.
for signal in audio_file_pre_save_signals:
    signals.pre_save.connect(receiver=AudioFile.pre_save_operations,
                             sender=signal['sender'],
                             dispatch_uid=signal['uid'])


class UserAudioFileSignal(CreatedTimeStampedModel):
    """
    Purpose: Keeping users' liked/not-liked (or yes/no answer'ed) audio files
    """
    class Meta:
        db_table = 'user_audio_file_signal'

    SIGNAL_POSITIVE = 'positive'
    SIGNAL_NEGATIVE = 'negative'

    SIGNAL_SET = (
        (SIGNAL_POSITIVE, 'Positive'),
        (SIGNAL_NEGATIVE, 'Negative'),
    )

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING,
                             related_name='liked_audio_files', )
    audio_file = models.ForeignKey(to=AudioFile,
                                   on_delete=models.DO_NOTHING,
                                   related_name='liked_by_users', )
    signal = models.CharField(max_length=50,
                              choices=SIGNAL_SET,
                              default=SIGNAL_POSITIVE, )

    @classmethod
    def is_signal_valid(cls, signal_type):
        return signal_type in [item[0] for item in cls.SIGNAL_SET]


class UserMainContentConsumption(CreatedTimeStampedModel):
    """
    Purpose: Keeping track of audio file consumption for all users.
    It is a unary entry, meaning that if there is an entry
    it means that it is assumed to be consumed.
    """
    class Meta:
        db_table = 'user_audio_consumption'
        ordering = ['id', ]

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING, )

    played_main_content = models.ForeignKey(to=AudioFile,
                                            on_delete=models.DO_NOTHING,
                                            null=True, )


class Messages(TimeStampedModel):
    """
    Purpose: Message Queue for actual messages, e.g. for text-to-speech and voice-mail
    """
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


class UserContentRepository(TimeStampedModel):
    """
    UserContentRepository is the user (senior-only) related states related the audio content, including:
        * injected_content_repository: JSON representing the state of Caressa device of the senior

    Use `get_for_user` function to fetch the entry for the user.
    Use `save_for_user` function to save an entry for the user.
    """

    class Meta:
        db_table = 'user_content_repository'

    user = models.OneToOneField(to=User,
                                primary_key=True,
                                null=False,
                                on_delete=models.CASCADE, )

    injected_content_repository = JSONField(default=[])

    @classmethod
    def save_for_user(cls, user: User, **kwargs) -> 'UserContentRepository':
        """
        Save an entry partially for the given user (senior-only).
        It is a partial update, meaning that provide as little as you need.
        Example:

        UserContentRepository.save_for_user(user, field_one={'some': 'thing'}, field_three={'another': 'thing'})

        :param user: User
        :param kwargs:
        :return: UserContentRepository
        """
        user_model = get_user_model()
        assert user.user_type == user_model.CARETAKER, (
            "UserContentRepository is only available for senior user type"
        )
        obj, _ = cls.objects.update_or_create(user=user, defaults=kwargs)
        return obj

    @classmethod
    def get_for_user(cls, user: User) -> 'UserContentRepository':
        user_model = get_user_model()
        assert user.user_type == user_model.CARETAKER, (
            "UserContentRepository is only available for senior user type"
        )
        obj, _ = cls.objects.get_or_create(user=user)
        return obj
