from rest_framework import serializers
from caressa.settings import REST_FRAMEWORK

from alexa.models import User
from alexa.api.serializers import SeniorSerializer
from senior_living_facility.models import SeniorLivingFacility, SeniorDeviceUserActivityLog, \
    SeniorLivingFacilityContent, ContentDeliveryRule, ServiceRequest
from senior_living_facility.models import SeniorLivingFacilityMockUserData as MockUserData
from senior_living_facility.models import SeniorLivingFacilityMockMessageData as MockMessageData
from utilities.logger import log
from utilities.views.mixins import MockStatusMixin, ForAdminApplicationMixin


class SeniorLivingFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SeniorLivingFacility
        fields = ('pk', 'name', 'facility_id', 'calendar_url', 'timezone',
                  'check_in_morning_start', 'check_in_deadline', 'check_in_reminder', )
        read_only_fields = ('facility_id', 'calendar_url', 'timezone', )


class FacilitySerializer(serializers.ModelSerializer, MockStatusMixin, ForAdminApplicationMixin):
    class Meta:
        model = SeniorLivingFacility
        fields = ('id',
                  'name',
                  'number_of_residents',
                  'number_of_unread_notifications',
                  'timezone',
                  'photo_gallery_url',
                  'profile_picture',
                  'mock_status', )
        read_only_fields = ('name', 'timezone', )

    number_of_residents = serializers.SerializerMethodField()
    number_of_unread_notifications = serializers.SerializerMethodField()
    photo_gallery_url = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_picture(facility: SeniorLivingFacility):
        return facility.get_profile_pic()

    @staticmethod
    def get_number_of_residents(facility: SeniorLivingFacility):  # todo hardcode
        return 142

    @staticmethod
    def get_number_of_unread_notifications(facility: SeniorLivingFacility):  # todo hardcode
        return 3

    @staticmethod
    def get_photo_gallery_url(facility: SeniorLivingFacility):  # todo hardcode
        return 'https://www.caressa.herokuapp.com/gallery_url'


class AdminAppSeniorListSerializer(SeniorSerializer, MockStatusMixin, ForAdminApplicationMixin):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no',
                  'device_status',
                  'message_thread_url',
                  'profile_picture',
                  'mock_status',
                  )

    device_status = serializers.SerializerMethodField()
    message_thread_url = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()

    @staticmethod
    def get_message_thread_url(senior: User):  # todo hardcode
        return 'https://caressa.herokuapp.com/senior-id-{id}-message-thread-url'.format(id=senior.id)

    @staticmethod
    def get_profile_picture(senior: User):
        return senior.get_profile_pic()

    @staticmethod
    def get_device_status(senior: User):
        mock_device_status = MockUserData.objects.all().filter(senior=senior)[0].device_status
        if mock_device_status == {}:
            return None
        return mock_device_status


class MorningCheckinUserNotifiedSerializer(AdminAppSeniorListSerializer, MockStatusMixin, ForAdminApplicationMixin):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no',
                  'device_status',
                  'message_thread_url',
                  'mock_status',
                  'check_in_info',
                  )

    check_in_info = serializers.SerializerMethodField()

    @staticmethod
    def get_check_in_info(senior: User):
        return {
            'check_in_url': 'https://caressa.herokuapp.com/senior-id-{id}-check-in-url'.format(id=senior.id)
        }


class FacilityMessagesSerializer(serializers.ModelSerializer, MockStatusMixin, ForAdminApplicationMixin):
    class Meta:
        model = MockMessageData
        fields = ('id', 'resident', 'last_message', 'mock_status', 'message_from')

    resident = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    message_from = serializers.SerializerMethodField()

    @staticmethod
    def get_resident(mock_message_data: MockMessageData):
        if not mock_message_data.senior:
            return 'All Residents'
        return AdminAppSeniorListSerializer(mock_message_data.senior).data

    @staticmethod
    def get_last_message(mock_message_data: MockMessageData):
        return mock_message_data.message

    @staticmethod
    def get_message_from(mock_message_data: MockMessageData):
        return mock_message_data.message_from


class MorningCheckinUserPendingSerializer(AdminAppSeniorListSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no',
                  'device_status',
                  'message_thread_url',
                  'mock_status',
                  'check_in_info',
                  )

    check_in_info = serializers.SerializerMethodField()

    @staticmethod
    def get_check_in_info(senior: User):
        return {
            'check_in_url': 'https://caressa.herokuapp.com/senior-id-{id}-check-in-url'.format(id=senior.id)
        }


class MorningCheckinUserStaffCheckedSerializer(AdminAppSeniorListSerializer, MockStatusMixin, ForAdminApplicationMixin):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no',
                  'device_status',
                  'message_thread_url',
                  'mock_status',
                  'check_in_info',
                  )

    check_in_info = serializers.SerializerMethodField()

    @staticmethod
    def get_check_in_info(senior: User):
        return {
            'checked_by': 'Staff Joe',
            'check_in_time': '2019-02-02T23:37:43.811630Z',
            'remove_check_in_url': 'https://caressa.herokuapp.com/senior-id-{id}-remove-check-in-url'.format(id=senior.id)
        }


class MorningCheckinUserSelfCheckedSerializer(AdminAppSeniorListSerializer, MockStatusMixin, ForAdminApplicationMixin):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no',
                  'device_status',
                  'message_thread_url',
                  'mock_status',
                  'check_in_info',
                  )

    check_in_info = serializers.SerializerMethodField()

    @staticmethod
    def get_check_in_info(senior: User):
        return {
            'checked_by': 'self',
            'check_in_time': '2019-02-02T23:37:43.811630Z'
        }

    @staticmethod
    def get_resident(obj):
        return {
            "pk": 94,
            "first_name": "Edward",
            "last_name": "Hofferton",
            "room_no": "106",
            "device_status": {
                "is_online": True,
                "status_checked": "2019-02-02T23:37:43.811630Z",
                "last_activity_time": "2019-03-22T03:59:08.302690Z",
                "is_today_checked_in": True
            },
            "message_thread_url": "https://caressa.herokuapp.com/senior-id-94-message-thread-url",
            "profile_picture": "https://s3-us-west-1.amazonaws.com/caressa-prod/images/user/no_user/default_profile_pic_w_250.jpg",
            "mock_status": True
        }


class MessageThreadMessagesSerializer(serializers.ModelSerializer, MockStatusMixin):
    class Meta:
        model = MockMessageData
        fields = ('id', 'message', 'mock_status', 'message_from')

    message = serializers.SerializerMethodField()
    message_from = serializers.SerializerMethodField()

    @staticmethod
    def get_message(mock_message_data: MockMessageData):
        return mock_message_data.message

    @staticmethod
    def get_message_from(mock_message_data: MockMessageData):
        return mock_message_data.message_from


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


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = ('requester', 'receiver', )
        read_only_fields = ('requester', 'receiver', )

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['requester'] = user
        validated_data['receiver'] = user.senior_living_facility
        instance = super(ServiceRequestSerializer, self).create(validated_data)     # type: ServiceRequest
        instance.process()
        return instance
