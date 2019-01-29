from django.contrib import admin
from senior_living_facility.models import SeniorLivingFacility


@admin.register(SeniorLivingFacility)
class SeniorLivingFacilityAdmin(admin.ModelAdmin):
    fields = ('name',
              'facility_id',
              'created',
              'modified', )
    list_display = ('id',
                    'name',
                    'facility_id', )
    readonly_fields = ('id',
                       'created',
                       'modified', )