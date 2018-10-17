from django.contrib import admin
from senior_living_facility.models import SeniorLivingFacility


class ResidentsInline(admin.TabularInline):
    model = SeniorLivingFacility.residents.through


@admin.register(SeniorLivingFacility)
class SeniorLivingFacilityAdmin(admin.ModelAdmin):
    fields = ('name',
              'facility_id',
              'created',
              'modified', )
    list_display = ('id',
                    'name',
                    'facility_id',
                    'number_of_residents', )
    readonly_fields = ('id',
                       'created',
                       'modified', )
    inlines = [
        ResidentsInline,
    ]
