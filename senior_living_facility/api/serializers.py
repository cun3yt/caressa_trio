from rest_framework import serializers
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog


class SeniorLivingFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorLivingFacility
        fields = ('pk', 'name', 'facility_id', 'calendar_url', 'timezone',
                  'check_in_morning_start', 'check_in_deadline', 'check_in_reminder', )
        read_only_fields = ('facility_id', 'calendar_url', 'timezone', )


class SeniorDeviceUserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorDeviceUserActivityLog
        fields = ('pk', 'user', 'activity', 'data', )

    data = serializers.JSONField()

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super(SeniorDeviceUserActivityLogSerializer, self).create(validated_data)
