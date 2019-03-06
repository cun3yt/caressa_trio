import pytz

from django.db import models
from django.utils.timezone import localtime
from model_utils.models import TimeStampedModel
from django.contrib.auth import get_user_model
from caressa.settings import TIME_ZONE as DEFAULT_TIMEZONE
from jsonfield import JSONField
from typing import Union


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
    check_in_morning_start = models.TimeField(null=True,
                                              default='05:30:00', )
    check_in_deadline = models.TimeField(null=True,
                                         default=None, )
    check_in_reminder = models.TimeField(null=True,
                                         default=None, )

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

    def __str__(self):
        return self.name


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


class SeniorDeviceUserActivityLog(TimeStampedModel):
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
    def get_last_user_log(cls, senior) -> Union['SeniorDeviceUserActivityLog', None]:
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
        activity_time_in_tz = localtime(self.created,
                                        timezone=pytz.timezone(facility.timezone))

        now_in_tz = localtime(timezone=pytz.timezone(facility.timezone))
        check_in_time_today_in_tz = now_in_tz.replace(hour=facility.check_in_morning_start.hour,
                                                      minute=facility.check_in_morning_start.minute,
                                                      second=0,
                                                      microsecond=0)

        return check_in_time_today_in_tz < activity_time_in_tz
