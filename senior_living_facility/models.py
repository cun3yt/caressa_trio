from django.db import models
from django.db.models import signals
from model_utils.models import TimeStampedModel, StatusField
from model_utils import Choices
from alexa.models import User
from utilities.logger import log
from datetime import datetime
from icalevents.icalevents import events as query_events
from voice_service.google.tts import tts_to_s3
from caressa.settings import TIME_ZONE as DEFAULT_TIMEZONE
import pytz
import hashlib


class SeniorLivingFacility(TimeStampedModel):
    class Meta:
        db_table = 'senior_living_facility'
        verbose_name = 'Senior Living Facility'
        verbose_name_plural = 'Senior Living Facilities'

    name = models.CharField(max_length=160, null=False, blank=False, )
    facility_id = models.CharField(max_length=200,
                                   null=False,
                                   blank=False,
                                   default='',
                                   unique=True,
                                   help_text='text identifier specifying location, too: e.g.'
                                             ' CA.Fremont.Brookdale', )
    residents = models.ManyToManyField(User, related_name='senior_living_facilities', )
    calendar_url = models.URLField(null=True, blank=False, default=None)
    timezone = models.CharField(max_length=200,
                                null=False,
                                blank=False,
                                default=DEFAULT_TIMEZONE, )

    @property
    def number_of_residents(self):
        return self.residents.count()

    def today_event_summary(self) -> 'SeniorLivingFacilityContent':
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)

        summary = "Today is {}. ".format(now.strftime('%B %d %A'))
        zero_state_summary = "{}Have a nice day at {}.".format(summary, self.name)

        if self.calendar_url is None:
            log('SeniorLivingFacility::today_event_summary() is called '
                'for empty calendar_url, SeniorLivingFacility entry id: {}'.format(self.id))
            return SeniorLivingFacilityContent.find(senior_living_facility=self,
                                                    text_content=zero_state_summary,
                                                    content_type='Daily-Calendar-Summary', )

        events = query_events(url=self.calendar_url,
                              start=datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=tz),
                              end=datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=tz),
                              fix_apple=True)

        all_day_events = [event for event in events if event.all_day]
        hourly_events = sorted([event for event in events if not event.all_day], key=lambda event: event.start)

        if len(events) == 0:
            return SeniorLivingFacilityContent.find(senior_living_facility=self,
                                                    text_content=zero_state_summary,
                                                    content_type='Daily-Calendar-Summary', )

        summary = "{}Here is today's schedule at {}: ".format(summary, self.name)

        for event in hourly_events:
            start_in_tz = event.start.astimezone(tz)
            event_txt = "At {}: {}. ".format(start_in_tz.strftime('%I:%M %p'), event.summary)
            summary = "{}{}".format(summary, event_txt)

        if len(all_day_events) == 1:
            summary = "{}There is a special thing for today: {}".format(summary, all_day_events[0].summary)
        elif len(all_day_events) > 1:
            summary = "{}There are {} special things for today: ".format(summary, len(all_day_events))
            for (no, event) in enumerate(all_day_events, start=1):
                summary = "{} ({}) {}.".format(summary, no, event.summary)

        return SeniorLivingFacilityContent.find(senior_living_facility=self,
                                                text_content=summary,
                                                content_type='Daily-Calendar-Summary', )


class SeniorLivingFacilityContent(TimeStampedModel):
    class Meta:
        db_table = 'senior_living_facility_content'
        index_together = ('senior_living_facility', 'text_content', 'content_type', )

    CONTENT_TYPES = Choices('Daily-Calendar-Summary', 'Event')

    senior_living_facility = models.ForeignKey(to=SeniorLivingFacility,
                                               null=False,
                                               blank=False,
                                               default=None,
                                               on_delete=models.DO_NOTHING, )
    content_type = StatusField(choices_name='CONTENT_TYPES',
                               null=False,
                               blank=False, )
    text_content = models.TextField(null=False,
                                    blank=True,
                                    default='', )
    text_content_hash = models.TextField(null=False,
                                         blank=True,
                                         default='',
                                         db_index=True, )
    audio_url = models.URLField(null=False,
                                blank=True,
                                default='', )

    @staticmethod
    def find(**kwargs) -> 'SeniorLivingFacilityContent':
        return SeniorLivingFacilityContent.objects.get_or_create(**kwargs)


def compute_hash_for_text_content(sender, instance, raw, using, update_fields, **kwargs):
    instance.hash = hashlib.sha256(instance.text_content.encode('utf-8')).hexdigest() if instance.text_content else ''
    instance.audio_url = tts_to_s3(text=instance.text_content) if instance.text_content else ''


signals.pre_save.connect(receiver=compute_hash_for_text_content,
                         sender=SeniorLivingFacilityContent, dispatch_uid='compute_hash_for_text_content')


class SeniorActOnFacilityContent(TimeStampedModel):
    class Meta:
        db_table = 'senior_act_on_facility_content'
        verbose_name = 'Senior\' Act On Facility Content'
        verbose_name_plural = 'Seniors\' Acts On Facility Content'
        index_together = ('senior', 'act', 'content', )

    ACTS = Choices('Heard', 'RSVP:Yes')

    senior = models.ForeignKey(User, null=False, blank=False, default=None, on_delete=models.DO_NOTHING)
    act = StatusField(choices_name='ACTS', null=False, blank=False, default=None)
    content = models.ForeignKey(SeniorLivingFacilityContent, null=False, blank=False, default=None,
                                on_delete=models.DO_NOTHING)


SeniorActOnFacilityContent._meta.get_field('created').db_index = True
