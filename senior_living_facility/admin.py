from django.contrib import admin
from senior_living_facility.models import SeniorLivingFacility, SeniorDevice, \
    SeniorLivingFacilityMockUserData


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


@admin.register(SeniorDevice)
class SeniorDeviceAdmin(admin.ModelAdmin):
    fields = ('serial', 'user', 'is_online', 'status_checked', )
    list_display = ('serial', 'user', 'is_online', 'status_checked', )
    readonly_fields = ('serial', 'is_online', 'status_checked', )


@admin.register(SeniorLivingFacilityMockUserData)
class SeniorLivingFacilityMockUserDataAdmin(admin.ModelAdmin):
    fields = ('checkin_status', 'senior', 'checkin_info', 'device_status')
    list_display = ('checkin_status', 'senior', 'checkin_info', 'device_status')
