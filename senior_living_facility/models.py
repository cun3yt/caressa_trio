from django.db import models
from model_utils.models import TimeStampedModel
from alexa.models import User
from utilities.calendar import create_empty_calendar
from utilities.logger import log


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


def set_init_calendar_for_senior_living_facility(sender, instance, created, **kwargs):
    if not created:
        return
    senior_living_facility = instance    # type: SeniorLivingFacility
    senior_living_facility.create_initial_calendar()
