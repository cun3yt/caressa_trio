from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth import get_user_model
from caressa.settings import TIME_ZONE as DEFAULT_TIMEZONE


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

