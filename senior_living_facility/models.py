import re

import pytz

from copy import deepcopy
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import signals, Q, FilteredRelation
from django.utils import timezone
from django.utils.functional import cached_property
from model_utils.models import TimeStampedModel, StatusField

from caressa.settings import DATETIME_FORMATS, TIME_ZONE as DEFAULT_TIMEZONE
from alexa import models as alexa_models
from jsonfield import JSONField
from typing import Optional
from utilities.template import template_to_str
from model_utils import Choices
from streaming.models import AudioFile

from utilities.models.mixins import ProfilePictureMixin
from utilities.models.abstract_models import CreatedTimeStampedModel
from senior_living_facility.mixins import AudioFileAndDeliveryRuleMixin
from datetime import datetime, time, date, timedelta
from icalevents.icalevents import events as query_events
from utilities.speech import ssml_post_process

from utilities.real_time_communication import send_instance_message
from utilities.sms import send_sms
from utilities.time import time_today_in_tz as time_in_tz, today_in_tz, now_in_tz


class SeniorLivingFacility(TimeStampedModel, ProfilePictureMixin):
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
    profile_pic = models.TextField(blank=True, default='')

    @property
    def phone_numbers(self) -> list:
        User = get_user_model()
        users = User.objects.all().filter(senior_living_facility=self,
                                          user_type__in=(User.CAREGIVER, User.CAREGIVER_ORG, ), )
        return [user.phone_number for user in users if user.phone_number]

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

    @property
    def is_morning_status_changeable(self):
        """
        Can the morning status be changed, i.e. is the morning status in the changeable zone.
        """
        return True     # todo hardcoding for demo
        # return self.check_in_time_today_in_tz <= now_in_tz(self.timezone) <= self.deadline_in_time_today_in_tz

    @property
    def next_morning_status_cut_off_time(self):
        now = now_in_tz(self.timezone)
        if now <= self.check_in_time_today_in_tz:
            return self.check_in_time_today_in_tz
        if now <= self.deadline_in_time_today_in_tz:
            return self.deadline_in_time_today_in_tz
        return self.check_in_time_today_in_tz + timedelta(days=1)

    def has_check_in_reminder_passed(self):     # todo get rid of `tz` for comparison
        assert self.check_in_reminder, (
            "check_in_reminder must be set in SeniorLivingFacility "
            "for has_check_in_reminder_passed function to be used."
        )
        check_in_reminder_in_tz = self.time_today_in_tz(self.check_in_reminder)
        return check_in_reminder_in_tz <= now_in_tz(self.timezone)

    def get_facility_realtime_channel(self):
        return alexa_models.User.get_facility_channel(self.facility_id)

    @property
    def real_time_communication_channels(self):
        channel = self.get_facility_realtime_channel()

        return {
            'check-in': {
                'channel': channel,
                'event': 'check-in-status',
            },
            'device-status': {
                'channel': channel,
                'event': 'device-status',
            }
        }

    @cached_property
    def resident_ids_self_checked_in_today(self):
        user_model = get_user_model()
        morning_check_in_time = self.check_in_time_today_in_tz.strftime('%Y-%m-%d %H:%M:%S%z')

        checked_in_senior_ids = list(user_model.objects.filter(senior_living_facility=self,
                                                               user_type__exact=user_model.CARETAKER,
                                                               device_user_logs__created__gt=morning_check_in_time)
                                     .distinct().values_list('id', flat=True))
        return checked_in_senior_ids

    def get_resident_ids_with_device_but_not_checked_in(self):
        user_model = get_user_model()
        checked_in_senior_ids = self.resident_ids_self_checked_in_today
        result_list = list(user_model.objects.filter(senior_living_facility=self,
                                                     user_type__exact=user_model.CARETAKER,
                                                     devices__isnull=False)
                           .exclude(id__in=checked_in_senior_ids)
                           .values_list('id', flat=True))
        return result_list

    def get_given_day_events(self, time_: datetime) -> dict:
        spoken_time_format = DATETIME_FORMATS['spoken']['time']

        tz = pytz.timezone(self.timezone)

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
                              start=datetime(time_.year, time_.month, time_.day, 0, 0, 0, tzinfo=tz),
                              end=datetime(time_.year, time_.month, time_.day, 23, 59, 59, tzinfo=tz),
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

    def get_today_events(self) -> dict:
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)
        return self.get_given_day_events(now)

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

    @cached_property
    def residents_grouped_by_state(self) -> dict:
        return FacilityCheckInOperationForSenior.get_seniors_grouped_by_state(facility=self)

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

    # Instead of `devices` use `User.device` property
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

    Purpose: Keeping the analytic logs of all interface of the senior device.

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
    """
    Purpose: Content Delivery Rule for Senior Device

    It includes:
        * Type: How the content is delivered, e.g. injectable (to main player), voice-mail, urgent-mail
        * Recipients: Which users to get the message
        * Start/End Datetime: The time interval the content is valid
        * Delivery Frequency: How often the related content is going to be delivered
    """
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

    # `recipient_ids = None` means the largest possible set (i.e. whole facility)
    recipient_ids = ArrayField(models.IntegerField(), null=True, default=None)

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


class SeniorLivingFacilityContent(CreatedTimeStampedModel, AudioFileAndDeliveryRuleMixin):
    """
    Purpose: Keeping the Auto-generated TTS content from the Senior Living Facility to the senior devices.
    Example contents:
        * Calendar Summary
        * Calendar Event
        * Morning Check-in Call to Action

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

    def get_text_content(self):
        return self.text_content

    def get_content_type(self):
        return self.content_type

    def get_payload_for_audio_file(self):
        return {'text': self.get_text_content(),
                'facility_id': self.senior_living_facility.id}

    def get_audio_type(self):
        return AudioFile.TYPE_FACILITY_AUTO_GENERATED_CONTENT


signals.pre_save.connect(receiver=SeniorLivingFacilityContent.pre_save_operations,
                         sender=SeniorLivingFacilityContent,
                         dispatch_uid='senior_living_facility_content.pre_save')


class SeniorLivingFacilityMessageLog(CreatedTimeStampedModel):
    """
    This model keeps track of the message/content that is sent by a `SeniorLivingFacility` at a given timestamp.

    Content Type: Definition of the content, e.g. 'Call for Morning Check In'
    Medium Type: Text-to-Speech, Voice
    Delivery Type: Urgent Mail, Voice Mail

    Example usage: Checking if the morning check in is sent in the last X hours.
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


class ServiceRequest(CreatedTimeStampedModel):
    """
    Purpose: Keeping The Logs of Service Button Press on Senior Device
    """
    class Meta:
        db_table = 'service_request'

    requester = models.ForeignKey(to='alexa.User',
                                  help_text="The user who requested the service "
                                            "(i.e. pressed the request button on the hardware)",
                                  on_delete=models.DO_NOTHING, )
    receiver = models.ForeignKey(to=SeniorLivingFacility,
                                 help_text="The facility that is in charge of fulfilling the service request",
                                 on_delete=models.DO_NOTHING, )

    def process(self):
        facility = self.receiver
        phone_numbers = facility.phone_numbers
        time_format = DATETIME_FORMATS['spoken']['time']
        tz = pytz.timezone(facility.timezone)
        request_time = self.created.astimezone(tz).strftime(time_format)
        context = {
            'name': self.requester.full_name,
            'room_no': self.requester.room_no,
            'time': request_time,
        }
        for number in phone_numbers:
            send_sms(number.as_international, context, 'sms/service-request.txt')


class Message(CreatedTimeStampedModel, AudioFileAndDeliveryRuleMixin):
    """
    Purpose: Keeping the messages sent from the community app to the senior device.

    It includes both message types:
        1. `content` to be TTS'ed and audio to be stored in `audio_file`
        2. Audio recordings stored directly in `audio_file`
    """

    class Meta:
        db_table = 'message'
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created', ]),
        ]

    message_thread = models.ForeignKey(to='MessageThread',
                                       help_text='Collection of messages between related participants.',
                                       on_delete=models.DO_NOTHING, )

    content = models.TextField(blank=True,
                               default="",
                               help_text='Content which will be processed with text to speech.', )

    source_user = models.ForeignKey(to='alexa.User',
                                    help_text='The user who sent the message.',
                                    on_delete=models.DO_NOTHING, )

    is_response_expected = models.BooleanField(default=False, )

    def get_text_content(self):
        return self.content

    def get_content_type(self):
        return "Text" if self.get_text_content() else "Audio"

    def get_payload_for_audio_file(self):
        return {
            'text': self.get_text_content(),
        }

    def get_audio_type(self):
        return AudioFile.TYPE_FACILITY_MESSAGE

    @classmethod
    def pre_save_after_hook(cls, **kwargs):
        message = kwargs.get('instance')   # type: Message
        channel = message.source_user.senior_living_facility.get_facility_realtime_channel()

        delivery_rule = message.delivery_rule

        # todo fix this dirty naming problem
        event_name = re.sub('-', '_', delivery_rule.type)
        event_name = 'injectable_content' if event_name == 'injectable' else event_name

        send_instance_message(channel, event_name,
                              {
                                  'url': message.audio_url,
                                  'hash': message.hash,
                                  'is_selected_recipient_type': True,
                                  'selected_recipient_ids': delivery_rule.recipient_ids
                              })


signals.pre_save.connect(receiver=Message.pre_save_operations,
                         sender=Message,
                         dispatch_uid='message.pre_save')


class MessageResponse(TimeStampedModel):  # todo Not in use at the moment
    """
    Purpose: Keep the message responses that required a yes/no answer.
    """
    class Meta:
        db_table = 'message_response'

    from_user = models.ForeignKey(to='alexa.User',
                                  help_text='User who responses the message',
                                  on_delete=models.DO_NOTHING, )

    message = models.ForeignKey(to=Message,
                                help_text='Response Requested Message',
                                on_delete=models.DO_NOTHING, )

    response = models.NullBooleanField(help_text='Message response True represents Yes, '
                                                 'False Represents No, '
                                                 'Null represents No Reply',
                                       default=None, )


class MessageThread(CreatedTimeStampedModel):
    class Meta:
        db_table = 'message_thread'

    @staticmethod
    def get_or_create_new_thread(sender_user: 'alexa_models.User', receiver_user: Optional['alexa_models.User']):

        assert sender_user.is_provider(), (
            "Message Threads defined for community providers. "
            "It is {user_type} for User id: {user_id}".format(user_type=sender_user.user_type,
                                                              user_id=sender_user.id)
        )

        is_all_recipients = True if receiver_user is None else False

        sender_user_facility = sender_user.senior_living_facility
        qs = MessageThreadParticipant.objects.all().filter(user=receiver_user,
                                                           senior_living_facility=sender_user_facility)
        created = False
        if qs.count() == 0:
            message_thread = MessageThread.objects.create()
            created = True
            MessageThreadParticipant.objects.create(message_thread=message_thread,
                                                    user=receiver_user,
                                                    senior_living_facility=sender_user_facility,
                                                    is_all_recipients=is_all_recipients, )
        else:
            message_thread = qs[0].message_thread

        return message_thread, created

    @property
    def last_message(self):
        return Message.objects.filter(message_thread=self)[0]

    @property
    def resident_participant(self):
        message_thread_participant = MessageThreadParticipant.objects.get(message_thread=self)
        if not message_thread_participant.user:
            return 'All Residents'
        return message_thread_participant.user


class MessageThreadParticipant(CreatedTimeStampedModel):
    class Meta:
        db_table = 'message_thread_participant'
        ordering = ['-created']
        unique_together = ('user', 'senior_living_facility')

    message_thread = models.ForeignKey(to=MessageThread,
                                       on_delete=models.DO_NOTHING, )

    user = models.ForeignKey(to='alexa.User',
                             null=True,
                             help_text='Message thread participating user',
                             on_delete=models.DO_NOTHING, )

    senior_living_facility = models.ForeignKey(to=SeniorLivingFacility,
                                               help_text='Message thread participating senior living facility',
                                               on_delete=models.DO_NOTHING, )

    is_all_recipients = models.BooleanField(help_text='If true user field needs to be empty',
                                            default=False, )


class FacilityCheckInOperationForSenior(TimeStampedModel):
    """
    Facility's Operation (i.e. Action) on Senior's Daily Check In Status

    Senior's self check in (implied data from another source)
    takes precedence over this data source.

    This data can be "notified" and "staff checked".
    "Staff checked" takes precedence over "notified" when both exist.
    If neither exists it is pending.
    """

    class Meta:
        db_table = 'facility_check_in_operation_for_senior'
        indexes = [
            models.Index(fields=['senior', 'date', ]),
        ]

    set_of_statuses = {
        'staff-checked': {
            'status': 'staff-checked',
            'label': 'Staff Checked',
        },
        'self-checked': {
            'status': 'self-checked',
            'label': 'Self Checked',
        },
        'pending': {
            'status': 'pending',
            'label': 'Pending',
        },
        'notified': {
            'status': 'notified',
            'label': 'Notified',
        },
    }

    senior = models.ForeignKey(to='alexa.User',
                               null=False,
                               on_delete=models.DO_NOTHING,
                               related_name='facility_check_in_operations', )

    date = models.DateField(null=False,
                            help_text="Check in information date for senior.", )

    notified = models.DateField(null=True,
                                default=None, )

    checked = models.DateTimeField(null=True,
                                   default=None, )

    staff = models.ForeignKey(to='alexa.User',
                              null=True,
                              on_delete=models.DO_NOTHING,
                              help_text="The facility staff that made the check in", )

    @classmethod
    def get_for_senior_today(cls, senior) -> Optional['FacilityCheckInOperationForSenior']:
        facility = senior.senior_living_facility
        date = today_in_tz(facility.timezone)
        operations = senior.facility_check_in_operations.filter(date=date)
        return operations[0] if operations.count() > 0 else None

    @classmethod
    def get_seniors_grouped_by_state(cls, facility: SeniorLivingFacility) -> dict:
        seniors_grouped = deepcopy(cls.set_of_statuses)
        for status, val in cls.set_of_statuses.items():
            seniors_grouped[status]['residents'] = cls._get_seniors_in_state(facility, val['status'])\
                .order_by('first_name', 'room_no')
        return seniors_grouped

    @classmethod
    def _get_seniors_in_state(cls, facility: SeniorLivingFacility, state=None):
        """
        Returns list of users that are in the given state today

        :param facility:
        :param state: possible values: "pending", "notified", "staff-checked", "self-checked", None
        :return: QuerySet['User']
        """

        User = get_user_model()

        if state is None:
            return facility.residents

        self_checked_in_user_ids = facility.resident_ids_self_checked_in_today

        if state == 'self-checked':
            return User.objects.filter(pk__in=self_checked_in_user_ids)

        filter_dict = {
            'user_type': User.CARETAKER,
            'senior_living_facility': facility,
            'facility_check_in_operations__date': today_in_tz(facility.timezone),
        }
        exclude_dict = {
            'pk__in': self_checked_in_user_ids,
        }

        if state == 'staff-checked':
            filter_dict = {**filter_dict,
                           'facility_check_in_operations__checked__isnull': False,
                           }
            return User.objects.all().filter(**filter_dict).exclude(**exclude_dict)
        elif state == 'notified':
            filter_dict = {**filter_dict,
                           'facility_check_in_operations__checked__isnull': True,
                           'facility_check_in_operations__notified__isnull': False,
                           }
            return User.objects.all().filter(**filter_dict).exclude(**exclude_dict)
        elif state == 'pending':
            # Fetching the entries
            #   * either both `checked` and `notified` are None
            # OR
            #   * there is no entry at all

            # todo Simplify if you can

            qs = User.objects.annotate(check_in_op=FilteredRelation('facility_check_in_operations',
                                                                    condition=
                                                                    Q(facility_check_in_operations__date=today_in_tz(
                                                                        facility.timezone))))\
                .filter(
                (Q(user_type=User.CARETAKER)
                 & Q(senior_living_facility=facility)
                 & ~Q(pk__in=self_checked_in_user_ids)
                 & Q(check_in_op__checked__isnull=True)
                 & Q(check_in_op__notified__isnull=True))
                | (Q(user_type=User.CARETAKER)
                   & Q(senior_living_facility=facility)
                   & ~Q(pk__in=self_checked_in_user_ids)
                   & Q(check_in_op__id__isnull=True)))
            return qs
        else:
            raise Exception('Cannot compute!')


class PhotoGallery(CreatedTimeStampedModel):
    class Meta:
        db_table = 'photo_gallery'

    senior_living_facility = models.OneToOneField(to=SeniorLivingFacility,
                                                  primary_key=True,
                                                  null=False,
                                                  blank=False,
                                                  on_delete=models.DO_NOTHING, )


class Photo(TimeStampedModel):
    class Meta:
        db_table = 'photo'
        ordering = ['-date']

    photo_gallery = models.ForeignKey(to=PhotoGallery,
                                      null=False,
                                      blank=False,
                                      on_delete=models.DO_NOTHING,
                                      help_text="The gallery which the photo belongs to.")

    date = models.DateField(null=False,
                            blank=False,
                            default=date.today,
                            help_text="This date represents when the photo taken. If date can't be extracted from "
                                      "photo's metadata it will be set to today by default.")

    url = models.URLField(blank=False,
                          null=False,
                          verbose_name='Photo URL',
                          help_text='Photo URL, it must be publicly accessible')


class SeniorLivingFacilityFeatureFlags(TimeStampedModel):
    class Meta:
        db_table = 'senior_living_facility_feature_flags'

    senior_living_facility = models.OneToOneField(to=SeniorLivingFacility,
                                                  primary_key=True,
                                                  null=False,
                                                  blank=False,
                                                  on_delete=models.DO_NOTHING, )

    morning_check_in = models.BooleanField(default=False)

    @classmethod
    def get_feature_flags_for(cls, facility: SeniorLivingFacility):
        flags, _ = cls.objects.get_or_create(senior_living_facility=facility)
        return flags
