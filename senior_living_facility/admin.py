from django.contrib import admin
from senior_living_facility.models import SeniorLivingFacility, SeniorDevice


@admin.register(SeniorLivingFacility)
class SeniorLivingFacilityAdmin(admin.ModelAdmin):
    fields = ('name',
              'facility_id',
              'zip_code',
              'created',
              'modified', )
    list_display = ('id',
                    'name',
                    'facility_id',
                    'zip_code', )
    readonly_fields = ('id',
                       'created',
                       'modified', )


@admin.register(SeniorDevice)
class SeniorDeviceAdmin(admin.ModelAdmin):
    fields = ('serial', 'user', 'is_online', 'status_checked', )
    list_display = ('serial', 'user', 'is_online', 'status_checked', )
    readonly_fields = ('serial', 'is_online', 'status_checked', )
