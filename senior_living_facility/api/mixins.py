from django.urls import reverse

from alexa.models import User
from senior_living_facility.models import SeniorDeviceUserActivityLog, FacilityCheckInOperationForSenior
from rest_framework import serializers


class DeviceStatusSerializerMixin:
    """
    Purpose: Get the device status information for a senior. This is designed to be used with User model.
    The serializer that uses this mixin needs to include:

    1. `device_status` in its fields tuple.
    2. `device_status = serializers.SerializerMethodField()`
    """

    device_status = serializers.SerializerMethodField()

    @staticmethod
    def get_device_status(senior: User):
        defaults = {
            'is_there_device': False,
            'status': {}
        }

        device = senior.device

        if not device:
            return defaults

        defaults['is_there_device'] = True

        status = {
            'is_online': False,
            'status_checked': None,
            'last_activity_time': None,
            'is_today_checked_in': False,
        }

        last_user_log = SeniorDeviceUserActivityLog.get_last_user_log(senior)

        if last_user_log:
            facility = senior.senior_living_facility
            status = {**status, **{
                'last_activity_time': last_user_log.created,
                'is_today_checked_in': last_user_log.is_activity_counted_as_check_in(facility),
            }}

        status = {**status, **{
            'is_online': device.is_online,
            'status_checked': device.status_checked,
        }}

        return {**defaults, **{'status': status}}


class CheckInSerializerMixin:
    """
    Purpose: Get the check in information for a senior. This is designed to be used with User model.
    The serializer that uses this mixin needs to include:

    1. `check_in_info` in its fields tuple.
    2. `check_in_info = serializers.SerializerMethodField(method_name=<either one of the get-functions>)`
    """

    check_in_info = serializers.SerializerMethodField(method_name='get_check_in_info_for_checked_in')

    @staticmethod
    def get_info_for_checked_in(senior: User):
        # todo time consuming for all user? N+1 problem fix with fetch related!

        operation = FacilityCheckInOperationForSenior.get_for_senior_today(senior)

        check_in_info = {
            'url': reverse('morning-check-in', kwargs={'pk': senior.id})
        }

        if operation:
            check_in_info = {**check_in_info, **{
                'checked_by': "Staff {}".format(operation.staff.first_name),
                'check_in_time': operation.checked,
            }}

        return check_in_info

    @staticmethod
    def get_info_for_not_checked_in(senior: User):
        return {
            'url': reverse('morning-check-in', kwargs={'pk': senior.id})
        }


class MessageThreadUrlSerializerMixin:
    """
    Purpose: Get the message thread for a senior. This is designed to be used with User model.
    The serializer that uses this mixin needs to include:

    1. `message_thread_url` in its fields tuple.
    2. `message_thread_url = serializers.SerializerMethodField()`
    """

    message_thread_url = serializers.SerializerMethodField()

    @staticmethod
    def get_message_thread_url(senior: User):
        return {'url': reverse('message-thread', kwargs={'pk': senior.id})}


class ProfilePictureUrlSerializerMixin:
    """
    Purpose: Get the profile picture URL for a senior. This is designed to be used with User model.
    The serializer that uses this mixin needs to include:

    1. `profile_picture_url` in its fields tuple.
    2. `profile_picture_url = serializers.SerializerMethodField()`
    """

    profile_picture_url = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_picture_url(senior: User):
        return senior.get_profile_pic()


class MorningCheckInSerializerMixin(DeviceStatusSerializerMixin, CheckInSerializerMixin,
                                    MessageThreadUrlSerializerMixin, ProfilePictureUrlSerializerMixin, ):

    @classmethod
    def get_check_in_fields(cls):
        return cls.get_base_fields() + ('check_in_info', )

    @staticmethod
    def get_base_fields():
        return ('device_status',
                'check_in_info',
                'message_thread_url',
                'profile_picture_url',)
