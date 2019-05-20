from django.apps import apps
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField
from utilities.cryptography import compute_hash

from voice_service.google.tts import tts_to_s3


class CreatedTimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` field.
    """
    created = AutoCreatedField(_('created'))

    class Meta:
        abstract = True


class AudioFileAndDeliveryRuleMixin(models.Model):
    """
    Purpose: TTS and DeliveryRule needs are addressed for models like `SeniorLivingFacilityContent` and `Message`

    How to use this mixin:
        * Extend it
        * Implement the abstract methods
        * Connect the model using the pre_save signal, example:

        signals.pre_save.connect(
            receiver=SeniorLivingFacilityContent.pre_save_operations,
            sender=SeniorLivingFacilityContent,
            dispatch_uid='senior_living_facility_content.pre_save', )
    """

    class Meta:
        abstract = True

    # `audio_file` must be filled with pre-save signal if not specified already!
    audio_file = models.ForeignKey(to='streaming.AudioFile',
                                   null=True,
                                   blank=False,
                                   default=None,
                                   on_delete=models.DO_NOTHING, )

    delivery_rule = models.ForeignKey(to='senior_living_facility.ContentDeliveryRule',
                                      null=False,
                                      on_delete=models.DO_NOTHING, )

    def get_text_content(self):
        # todo for SeniorLivingFacilityContent this needs to be returned: `self.text_content`

        raise NotImplementedError("get_text_content function needed to be implemented by "
                                  "the class using `AudioFileAndDeliveryMixin`")

    def get_content_type(self):
        # todo for SeniorLivingFacilityContent this needs to be returned: `self.content_type`

        raise NotImplementedError("get_content_type function needed to be implemented by "
                                  "the class using `AudioFileAndDeliveryMixin`")

    def get_payload_for_audio_file(self):
        # todo for SeniorLivingFacilityContent this needs to be returned:
        #  {'text': self.get_text_content(),
        #   'facility_id': self.senior_living_facility.id}

        raise NotImplementedError("get_payload_for_audio_file function needed to be implemented by "
                                  "the class using `AudioFileAndDeliveryMixin`")

    def get_audio_type(self):
        # The audio_type that is set in `AudioType` instance
        raise NotImplementedError("get_audio_type function needed to be implemented by "
                                  "the class using `AudioFileAndDeliveryMixin`")

    @property
    def audio_url(self):
        assert self.audio_file, (
            "audio_file is not set"
        )
        return self.audio_file.url

    @property
    def hash(self):
        assert self.audio_file, (
            "audio_file is not set"
        )
        return self.audio_file.hash

    @classmethod
    def find(cls, delivery_type, start, end, frequency, recipient_ids=None, **kwargs):
        ContentDeliveryRule = apps.get_model('senior_living_facility.ContentDeliveryRule')

        delivery_rule = ContentDeliveryRule.find(delivery_type, start, end, frequency, recipient_ids)
        inst, _ = cls.objects.get_or_create(delivery_rule=delivery_rule, **kwargs)
        return inst

    def _generate_hash(self):
        txt = "{}-{}-{}".format(str(self.delivery_rule), self.get_text_content(), self.get_content_type())
        return compute_hash(txt)

    def set_audio_file(self, audio_type):
        if self.audio_file is not None:
            return

        url = tts_to_s3(return_format='url', text=self.get_text_content())

        AudioFile = apps.get_model('streaming.AudioFile')

        audio_file = AudioFile.objects.create(audio_type=audio_type,    # AudioFile.TYPE_FACILITY_AUTO_GENERATED_CONTENT
                                              url=url,
                                              payload=self.get_payload_for_audio_file(),
                                              hash=self._generate_hash())
        self.audio_file = audio_file

    @staticmethod
    def pre_save_operations(**kwargs):
        instance = kwargs.get('instance')
        audio_type = instance.get_audio_type()
        instance.set_audio_file(audio_type)
