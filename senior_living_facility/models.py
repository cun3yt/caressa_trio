from django.db import models
from model_utils.models import TimeStampedModel
from alexa.models import User
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
    calendar_url = models.URLField(null=True, blank=False, default=None)
    timezone = models.CharField(max_length=200,
                                null=False,
                                blank=False,
                                default=DEFAULT_TIMEZONE, )

    @property
    def number_of_residents(self):
        return self.residents.count()

    def today_event_summary(self) -> str:
        tz = pytz.timezone(self.timezone)
        now = datetime.now(tz)

        summary = "Today is {}. ".format(now.strftime('%B %d %A'))
        zero_state_summary = "{}Have a nice day at {}.".format(summary, self.name)

        if self.calendar_url is None:
            log('SeniorLivingFacility::today_event_summary() is called '
                'for empty calendar_url, SeniorLivingFacility entry id: {}'.format(self.id))
            return zero_state_summary

        events = query_events(url=self.calendar_url,
                              start=datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=tz),
                              end=datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=tz),
                              fix_apple=True)

        all_day_events = [event for event in events if event.all_day]
        hourly_events = sorted([event for event in events if not event.all_day], key=lambda event: event.start)

        if len(events) == 0:
            return zero_state_summary

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
