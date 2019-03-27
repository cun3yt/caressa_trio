import hashlib
import pytz

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import signals
from django.utils import timezone
from model_utils.models import TimeStampedModel, StatusField
from caressa.settings import TIME_ZONE as DEFAULT_TIMEZONE
from jsonfield import JSONField
from typing import Optional
from utilities.template import template_to_str
from model_utils import Choices

from utilities.views.mixins import ForAdminMixin
from voice_service.google.tts import tts_to_s3
from utilities.models.abstract_models import CreatedTimeStampedModel
from datetime import datetime, time, timedelta
from icalevents.icalevents import events as query_events
from utilities.speech import ssml_post_process

from utilities.time import time_today_in_tz as time_in_tz


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
    calendar_url = models.URLField(null=True, blank=True, default=None)
    timezone = models.CharField(max_length=200,
                                null=False,
                                blank=False,
                                default=DEFAULT_TIMEZONE, )
    check_in_morning_start = models.TimeField(null=False,
                                              default='05:30:00', )
    check_in_deadline = models.TimeField(null=False,
                                         default='10:00:00', )
    check_in_reminder = models.TimeField(null=True,
                                         default=None, )    # todo check business value of having default value

    @property
    def admins(self):
        user_model = get_user_model()
        return user_model.objects.filter(senior_living_facility=self,
                                         user_type__exact=user_model.CAREGIVER_ORG)

    @property
    def residents(self):
        user_model = get_user_model()
        return user_model.objects.filter(senior_living_facility=self,
                                         user_type__exact=user_model.CARETAKER)

    def time_today_in_tz(self, t: time):
        return time_in_tz(self.timezone, t.hour, t.minute)

    @property
    def check_in_time_today_in_tz(self):
        return self.time_today_in_tz(self.check_in_morning_start)

    @property
    def deadline_in_time_today_in_tz(self):
        return self.time_today_in_tz(self.check_in_deadline)

    def has_check_in_reminder_passed(self):     # todo get rid of `tz` for comparison
        assert self.check_in_reminder, (
            "check_in_reminder must be set in SeniorLivingFacility "
            "for has_check_in_reminder_passed function to be used."
        )
        check_in_reminder_in_tz = self.time_today_in_tz(self.check_in_reminder)
        now_in_tz = timezone.localtime(timezone=pytz.timezone(self.timezone))
        return check_in_reminder_in_tz <= now_in_tz

    def get_resident_ids_checked_in(self):
        user_model = get_user_model()
        morning_check_in_time = self.check_in_time_today_in_tz.strftime('%Y-%m-%d %H:%M:%S%z')

        checked_in_senior_ids = list(user_model.objects.filter(senior_living_facility=self,
                                                               user_type__exact=user_model.CARETAKER,
                                                               device_user_logs__created__gt=morning_check_in_time)
                                     .distinct().values_list('id', flat=True))
        return checked_in_senior_ids

    def get_resident_ids_with_device_but_not_checked_in(self):
        user_model = get_user_model()
        checked_in_senior_ids = self.get_resident_ids_checked_in()
        result_list = list(user_model.objects.filter(senior_living_facility=self,
                                                     user_type__exact=user_model.CARETAKER,
                                                     devices__isnull=False)
                           .exclude(id__in=checked_in_senior_ids)
                           .values_list('id', flat=True))
        return result_list

    def get_today_events(self):
        spoken_time_format = "%I:%M %p"  # e.g. '06:30 PM'

        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        events = {
            'count': 0,
            'all_day': {
                'count': 0,
                'set': [],
            },
            'hourly_events': {
                'count': 0,
                'set': [],
            },
        }

        if self.calendar_url:
            qs = query_events(url=self.calendar_url,
                              start=datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=tz),
                              end=datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=tz),
                              fix_apple=True)

            events['all_day']['set'] = [{'summary': event.summary,
                                         'location': event.description, }
                                        for event in qs if event.all_day]
            events['all_day']['count'] = len(events['all_day']['set'])

            events['hourly_events']['set'] = sorted([{'summary': event.summary,
                                                      'location': event.description,
                                                      'start': event.start,
                                                      'start_spoken':
                                                          event.start.astimezone(tz).strftime(spoken_time_format), }
                                                     for event in qs if not event.all_day],
                                                    key=lambda event: event['start'])
            events['hourly_events']['count'] = len(events['hourly_events']['set'])
            events['count'] = events['all_day']['count'] + events['hourly_events']['count']

        return events

    def today_events_summary_in_text(self) -> str:
        spoken_date_format = "%B %d %A"     # e.g. 'March 21 Thursday'

        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        today_formatted = now.strftime(spoken_date_format)

        events = self.get_today_events()

        context = {
            'today': today_formatted,
            'events': events,
            'facility_name': self.name,
            'zero_state': events['count'] == 0,
        }

        template_with_context = template_to_str('speech/whole-calendar-today.ssml', context)
        return ssml_post_process(template_with_context)

    def __str__(self):
        return self.name

    @staticmethod
    def get_text_for_hourly_event(event: dict, in_minutes_offset: int) -> str:
        """
        For a given dictionary of event it generated the text to be announced.

        :param event: Dictionary with 'summary', 'location', 'start', 'start_spoken' (e.g. "06:30 PM")
        :param in_minutes_offset: This is for announcement, e.g. "in 30 minutes"
        :return: str (the text to be announced)
        """

        summary = event.get('summary')
        start = event.get('start')
        start_spoken = event.get('start_spoken')
        location = event.get('location')
        assert all([summary, start, start_spoken]), (
            "`summary`, `start` and `start_spoken` must exist in the event dictionary"
        )

        context = {
            'summary': summary,
            'start': start,
            'start_spoken': start_spoken,
            'location': location,
            'in_minutes_offset': in_minutes_offset,
        }

        template_with_context = template_to_str('speech/hourly-calendar-event.ssml', context)
        return ssml_post_process(template_with_context)


class SeniorDevice(TimeStampedModel):
    """
    This class represents a Caressa Hardware
    Currently this only represents internet access of the devices.

    Todo this or something else needs to represent caressa-service's availability, too.
    """
    class Meta:
        db_table = 'senior_device'
        verbose_name = 'Senior Device'
        verbose_name_plural = 'Senior Devices'

    serial = models.CharField(primary_key=True, max_length=50, blank=True, default='', null=False, )
    user = models.ForeignKey(to='alexa.User', on_delete=models.DO_NOTHING, null=True, related_name='devices', )
    is_online = models.BooleanField(default=False, )
    status_checked = models.DateTimeField(null=False, )
    raw_log = models.ForeignKey(to='senior_living_facility.SeniorDevicesRawLog', null=True, on_delete=models.DO_NOTHING)

    @staticmethod
    def call_for_check_in_text():
        context = {
            'greeting': 'Hello',
        }
        return template_to_str('speech/call-for-check-in.ssml', context)


class SeniorDevicesRawLog(TimeStampedModel):
    """
    This class represents raw data fetched from senior devices.
    It is currently the raw API data from Dataplicity.
    """
    class Meta:
        db_table = 'senior_devices_raw_log'
        verbose_name = "Senior Devices' Raw Log"
        verbose_name_plural = "Senior Devices' Raw Logs"

    data = JSONField(default={})


class SeniorDeviceUserActivityLog(CreatedTimeStampedModel):
    """
    This class represents users' interaction with his/her device.

    Example activity log:
        activity: click.main-button
        data (extra/notes/payload): { 'device-response': 'pause.content' }
    """

    class Meta:
        db_table = 'senior_device_user_activity_log'
        verbose_name = "Senior Device User Activity Log"
        verbose_name_plural = "Senior Device User Activity Logs"

    user = models.ForeignKey(to='alexa.User', null=True, on_delete=models.DO_NOTHING, related_name='device_user_logs')
    activity = models.TextField(db_index=True)
    data = JSONField(default={})

    @classmethod
    def get_last_user_log(cls, senior) -> Optional['SeniorDeviceUserActivityLog']:
        logs = senior.device_user_logs.order_by('-id')
        if logs.count() == 0:
            return None
        return logs[0]

    def is_activity_counted_as_check_in(self, facility: SeniorLivingFacility):
        """
        compares this log's creation time to SeniorLivingFacility's daily check in start
        to decide if this user log is counted as check in.

        :param facility:
        :return: boolean
        """
        activity_time_in_tz = timezone.localtime(self.created,
                                                 timezone=pytz.timezone(facility.timezone))

        check_in_time_today_in_tz = facility.check_in_time_today_in_tz
        return check_in_time_today_in_tz < activity_time_in_tz


SeniorDeviceUserActivityLog._meta.get_field('created').db_index = True


class ContentDeliveryRule(models.Model):
    class Meta:
        db_table = 'content_delivery_rule'
        indexes = [
            models.Index(fields=['start', 'end', 'frequency', ])
        ]

    FREQUENCY_ONE_TIME = 'one-time'

    TYPE_INJECTABLE = 'injectable'
    TYPE_VOICE_MAIL = 'voice-mail'
    TYPE_URGENT_MAIL = 'urgent-mail'

    TYPES = Choices(TYPE_INJECTABLE, TYPE_VOICE_MAIL, TYPE_URGENT_MAIL, )

    type = StatusField(choices_name='TYPES', null=False, blank=False, default=TYPE_INJECTABLE)
    recipient_ids = ArrayField(models.IntegerField(), null=True, default=None) # None is the largest possible set (e.g. whole facility)
    start = models.DateTimeField(default=timezone.now, null=False, blank=False, )
    end = models.DateTimeField(null=False, blank=False, )
    frequency = models.IntegerField(help_text="Frequency in seconds. If the field is set to 0 "
                                              "it means that it is for one time use",
                                    default=0,
                                    null=False, )

    @classmethod
    def find(cls, delivery_type, start, end, frequency=FREQUENCY_ONE_TIME, recipient_ids=None) -> 'ContentDeliveryRule':
        frequency = 0 if frequency == cls.FREQUENCY_ONE_TIME else frequency
        inst, _ = cls.objects.get_or_create(type=delivery_type, start=start, end=end, frequency=frequency,
                                            recipient_ids=recipient_ids)
        return inst

    def __str__(self):
        return "ContentDeliveryRule({},{},{})".format(self.start.timestamp(), self.end.timestamp(), self.frequency)


class SeniorLivingFacilityContent(CreatedTimeStampedModel):
    """
    All text (tts) contents that are sent from SeniorLivingFacility to seniors are saved here.
    """
    class Meta:
        db_table = 'senior_living_facility_content'
        indexes = [
            models.Index(fields=['senior_living_facility', 'text_content', 'content_type', ])
        ]
        ordering = ('pk', )

    TYPE_DAILY_CALENDAR = 'Daily-Calendar'
    TYPE_CHECK_IN_CALL = 'Check-In-Call'
    TYPE_UPCOMING_INDIVIDUAL_EVENT = 'Upcoming-Individual-Event'

    CONTENT_TYPES = Choices(TYPE_DAILY_CALENDAR,
                            TYPE_CHECK_IN_CALL,
                            TYPE_UPCOMING_INDIVIDUAL_EVENT, )

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
    text_content_hash = models.TextField(null=False,    # todo the name better be changed to `hash`
                                         blank=True,
                                         default='',
                                         db_index=True, )
    audio_url = models.URLField(null=False,
                                blank=True,
                                default='', )
    delivery_rule = models.ForeignKey(to=ContentDeliveryRule,
                                      null=False,
                                      on_delete=models.DO_NOTHING, )

    @staticmethod
    def find(delivery_type, start, end, frequency=ContentDeliveryRule.FREQUENCY_ONE_TIME,
             recipient_ids=None, **kwargs) -> 'SeniorLivingFacilityContent':
        delivery_rule = ContentDeliveryRule.find(delivery_type, start, end, frequency, recipient_ids)
        inst, _ = SeniorLivingFacilityContent.objects.get_or_create(delivery_rule=delivery_rule, **kwargs)
        return inst


def compute_hash_for_text_content(sender, instance, raw, using, update_fields, **kwargs):
    txt = "{}-{}-{}".format(str(instance.delivery_rule), instance.text_content, instance.content_type)
    instance.text_content_hash = hashlib.sha256(txt.encode('utf-8')).hexdigest() \
        if instance.text_content else ''
    instance.audio_url = tts_to_s3(return_format='url', text=instance.text_content) if instance.text_content else ''


signals.pre_save.connect(receiver=compute_hash_for_text_content,
                         sender=SeniorLivingFacilityContent, dispatch_uid='compute_hash_for_text_content')


class SeniorLivingFacilityMessageLog(CreatedTimeStampedModel):
    """
    This model keeps track of the message/content that is sent by a `SeniorLivingFacility` at a given timestamp.

    Content Type: Definition of the content, e.g. 'Call for Morning Check In'
    Medium Type: Text-to-Speech, Voice
    Delivery Type: Urgent Mail, Voice Mail
    """
    class Meta:
        db_table = 'senior_living_facility_message_log'

    CONTENT_TYPE_CALL_FOR_MORNING_CHECK_IN = 'call-for-morning-check-in'
    CONTENT_TYPE_CUSTOM_MESSAGE = 'custom-message'

    CONTENT_TYPE_SET = (
        (CONTENT_TYPE_CALL_FOR_MORNING_CHECK_IN, 'Call for Morning Check In'),
        (CONTENT_TYPE_CUSTOM_MESSAGE, 'Custom Message'),
    )

    MEDIUM_TYPE_TEXT = 'text'
    MEDIUM_TYPE_VOICE = 'voice'

    MEDIUM_TYPE_SET = (
        (MEDIUM_TYPE_TEXT, 'Text'),
        (MEDIUM_TYPE_VOICE, 'Voice'),
    )

    DELIVERY_TYPE_URGENT_MAIL = 'urgent-mail'
    DELIVERY_TYPE_VOICE_MAIL = 'voice-mail'

    DELIVERY_TYPE_SET = (
        (DELIVERY_TYPE_URGENT_MAIL, 'Urgent Mail'),
        (DELIVERY_TYPE_VOICE_MAIL, 'Voice Mail'),
    )

    senior_living_facility = models.ForeignKey(to=SeniorLivingFacility,
                                               null=False,
                                               blank=False,
                                               default=None,
                                               on_delete=models.DO_NOTHING, )

    content_type = models.TextField(
        choices=CONTENT_TYPE_SET,
        null=False,
        blank=False,
        default=None, )

    medium_type = models.TextField(
        choices=MEDIUM_TYPE_SET,
        null=False,
        blank=False,
        default=None, )

    delivery_type = models.TextField(
        choices=DELIVERY_TYPE_SET,
        null=False,
        blank=False,
        default=None, )

    data = JSONField(default={})


SeniorLivingFacilityMessageLog._meta.get_field('created').db_index = True


class SeniorLivingFacilityMockUserData(TimeStampedModel, ForAdminMixin):
    class Meta:
        db_table = 'mock_user_data'

    NOTIFIED = 'NOTIFIED'
    PENDING = 'PENDING'
    STAFF_CHECKED = 'STAFF_CHECKED'
    SELF_CHECKED = 'SELF_CHECKED'

    TYPE_SET = (
        (NOTIFIED, 'Notified'),
        (PENDING, 'Pending'),
        (STAFF_CHECKED, 'Staff Checked'),
        (SELF_CHECKED, 'Self Checked'),
    )

    checkin_status = models.TextField(
        choices=TYPE_SET,
        default=PENDING,
    )

    senior = models.OneToOneField(to='alexa.User',
                                  primary_key=True,
                                  null=False,
                                  on_delete=models.DO_NOTHING,
                                  )

    checkin_info = JSONField(default={})

    device_status = JSONField(default={})
