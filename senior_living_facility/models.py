from django.db import models
from model_utils.models import TimeStampedModel
from alexa.models import User
from utilities.calendar import create_empty_calendar
from utilities.logger import log
from datetime import datetime
from icalevents.icalevents import events as query_events
from caressa.settings import TIME_ZONE as DEFAULT_TIMEZONE
import pytz


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
    calendar = models.TextField(null=False, blank=True, default="")
    timezone = models.CharField(max_length=200,
                                null=False,
                                blank=False,
                                default=DEFAULT_TIMEZONE, )

    def create_initial_calendar(self, override=False):
        if not self.calendar == '' and not override:
            raise ValueError('Calendar already set, you cannot re-initialize it')

        log('calendar is already set' if self.calendar else 'calendar is not set')
        log('override is ON' if override else 'override is OFF')

        self.calendar = create_empty_calendar(summary='Calendar of Facility:{}'.format(self.facility_id))
        self.save()

    @property
    def number_of_residents(self):
        return self.residents.count()

    def today_event_summary(self) -> str:
        tz = pytz.timezone(self.timezone)
        calendar = self.calendar.encode(encoding='UTF-8')

        now = datetime.now(tz)

        events = query_events(string_content=calendar,
                              start=datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=tz),
                              end=datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=tz),
                              fix_apple=True)

        all_day_events = [event for event in events if event.all_day]
        hourly_events = sorted([event for event in events if not event.all_day], key=lambda event: event.start)

        now_in_tz = now.astimezone(tz)
        summary = "Today is {}. ".format(now_in_tz.strftime('%B %d %A'))

        if len(events) == 0:
            summary = "{}We hope you have a great day at {}.".format(summary, self.name)
            return summary

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

        return summary


def set_init_calendar_for_senior_living_facility(sender, instance, created, **kwargs):
    if not created:
        return
    senior_living_facility = instance    # type: SeniorLivingFacility
    senior_living_facility.create_initial_calendar()
