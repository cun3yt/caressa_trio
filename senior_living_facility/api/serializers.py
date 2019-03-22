from rest_framework import serializers
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog
from utilities.logger import log


class SeniorLivingFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorLivingFacility
        fields = ('pk', 'name', 'facility_id', 'calendar_url', 'timezone',
                  'check_in_morning_start', 'check_in_deadline', 'check_in_reminder', )
        read_only_fields = ('facility_id', 'calendar_url', 'timezone', )


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorLivingFacility
        fields = ('name', 'number_of_residents', 'number_of_unread_notifications', 'timezone', 'photo_gallery_url', )
        read_only_fields = ('name', 'timezone', )

    number_of_residents = serializers.SerializerMethodField()
    number_of_unread_notifications = serializers.SerializerMethodField()
    photo_gallery_url = serializers.SerializerMethodField()

    def get_number_of_residents(self, facility: SeniorLivingFacility):  # todo hardcode
        log(facility)
        return 142

    def get_number_of_unread_notifications(self, facility: SeniorLivingFacility):  # todo hardcode
        log(facility)
        return 3

    def get_photo_gallery_url(self, facility: SeniorLivingFacility):  # todo hardcode
        log(facility)
        return 'https://www.caressa.herokuapp.com/gallery_url'


class SeniorDeviceUserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorDeviceUserActivityLog
        fields = ('pk', 'user', 'activity', 'data', )

    data = serializers.JSONField()

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super(SeniorDeviceUserActivityLogSerializer, self).create(validated_data)
