from rest_framework import serializers
from senior_living_facility.models import SeniorLivingFacilityContent, ContentDeliveryRule
from caressa.settings import REST_FRAMEWORK

from alexa.models import User
from alexa.api.serializers import SeniorSerializer
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog
from utilities.logger import log
from utilities.views.mixins import MockStatusMixin, ForAdminMixin


class SeniorLivingFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorLivingFacility
        fields = ('pk', 'name', 'facility_id', 'calendar_url', 'timezone',
                  'check_in_morning_start', 'check_in_deadline', 'check_in_reminder', )
        read_only_fields = ('facility_id', 'calendar_url', 'timezone', )


class FacilitySerializer(serializers.ModelSerializer, MockStatusMixin):
    class Meta:
        model = SeniorLivingFacility
        fields = ('name',
                  'number_of_residents',
                  'number_of_unread_notifications',
                  'timezone',
                  'photo_gallery_url',
                  'mock_status', )
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


class AdminAppSeniorListSerializer(SeniorSerializer, MockStatusMixin, ForAdminMixin):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'room_no', 'device_status', 'message_thread_url', 'mock_status')

    device_status = serializers.SerializerMethodField()
    message_thread_url = serializers.SerializerMethodField()

    @staticmethod
    def get_message_thread_url(senior: User):  # todo hardcode
        return 'https://caressa.herokuapp.com/senior-id-{id}-message-thread-url'.format(id=senior.id)


class MorningCheckingUserNotifiedSerializer(AdminAppSeniorListSerializer, MockStatusMixin, ForAdminMixin):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'room_no', 'device_status', 'message_thread_url', 'mock_status', 'notified')

    notified = serializers.SerializerMethodField()

    @staticmethod
    def get_notified(senior: User):
        log(senior)
        return 'Notified!'


class MorningCheckingUserStaffCheckedSerializer(AdminAppSeniorListSerializer, MockStatusMixin, ForAdminMixin):
    pass


class MorningCheckingUserSelfCheckedSerializer(AdminAppSeniorListSerializer, MockStatusMixin, ForAdminMixin):
    pass


class MorningCheckingUserPendingSerializer(AdminAppSeniorListSerializer):
    pass


class SeniorDeviceUserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorDeviceUserActivityLog
        fields = ('pk', 'user', 'activity', 'data', )

    data = serializers.JSONField()

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super(SeniorDeviceUserActivityLogSerializer, self).create(validated_data)


class ContentDeliveryRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentDeliveryRule
        fields = ('start', 'end', 'frequency', )

    start = serializers.DateTimeField(REST_FRAMEWORK['DATETIME_ZONE_FORMAT'])
    end = serializers.DateTimeField(REST_FRAMEWORK['DATETIME_ZONE_FORMAT'])


class SeniorLivingFacilityContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorLivingFacilityContent
        fields = ('hash', 'audio_url', 'delivery_rule', )

    hash = serializers.SerializerMethodField()
    delivery_rule = ContentDeliveryRuleSerializer()

    @staticmethod
    def get_hash(content: SeniorLivingFacilityContent):
        return content.text_content_hash
