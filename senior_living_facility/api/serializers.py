from datetime import timedelta

from django.utils import timezone

from rest_framework import serializers
from caressa.settings import REST_FRAMEWORK

from alexa.models import User
from senior_living_facility.api import mixins as facility_mixins
from senior_living_facility import models as facility_models
from alexa.api.serializers import UserSerializer
from senior_living_facility.models import ContentDeliveryRule, ServiceRequest, Message, MessageThread
from streaming.models import AudioFile
from utilities.api.urls import reverse
from utilities.aws_operations import move_file_from_upload_to_prod_bucket


class SeniorLivingFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.SeniorLivingFacility
        fields = ('pk', 'name', 'facility_id', 'calendar_url', 'timezone',
                  'check_in_morning_start', 'check_in_deadline', 'check_in_reminder', )
        read_only_fields = ('facility_id', 'calendar_url', 'timezone', )


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.SeniorLivingFacility
        fields = ('id',
                  'name',
                  'number_of_residents',
                  'timezone',
                  'photo_gallery_url',
                  'profile_picture',
                  'real_time_communication_channels',
                  'feature_flags', )
        read_only_fields = ('name', 'timezone', )

    number_of_residents = serializers.SerializerMethodField()
    photo_gallery_url = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()
    feature_flags = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_picture(facility: facility_models.SeniorLivingFacility):
        return facility.get_profile_pic()

    @staticmethod
    def get_number_of_residents(facility: facility_models.SeniorLivingFacility):
        return facility.residents.count()

    @staticmethod
    def get_photo_gallery_url(facility: facility_models.SeniorLivingFacility):
        return reverse('photo-gallery', kwargs={'pk': facility.id})

    @staticmethod
    def get_feature_flags(facility: facility_models.SeniorLivingFacility):
        feature_flags = facility_models.SeniorLivingFacilityFeatureFlags.get_feature_flags_for(facility=facility)
        return FacilityFeatureFlagsSerializer(feature_flags).data


class FacilityFeatureFlagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.SeniorLivingFacilityFeatureFlags
        fields = ('morning_check_in', )


class FacilityMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id',
                  'content',
                  'content_audio_file',
                  'is_response_expected', )

    content_audio_file = serializers.SerializerMethodField()

    @staticmethod
    def get_content_audio_file(message: facility_models.Message):
        return message.audio_url

    def create(self, validated_data):
        source_user = self.context['request'].user
        receiver_user_id = self.context['request'].data['to']

        receiver_user = None if receiver_user_id == 'all-residents' else User.objects.get(id=receiver_user_id)

        validated_data['message_thread'], _ = MessageThread.get_or_create_new_thread(source_user, receiver_user)
        validated_data['source_user'] = source_user

        message_data = self.context['request'].data['message']
        message_format = message_data.get('format')

        if message_format == 'text':
            text_content = message_data.get('content')
        else:
            text_content = ""
            source_file_key = message_data.get('content')
            dest_file_key = 'audio/facility/{id}/message/{key}'.format(id=source_user.senior_living_facility.id,
                                                                       key=source_file_key)

            audio_url = move_file_from_upload_to_prod_bucket(source_file_key=source_file_key,
                                                             dest_file_key=dest_file_key)
            audio_file = AudioFile.objects.create(audio_type=AudioFile.TYPE_FACILITY_MESSAGE,
                                                  url=audio_url, )

            validated_data['audio_file'] = audio_file

        validated_data['content'] = text_content

        message_types = {
            "Message": 'voice-mail',
            "Broadcast": 'urgent-mail',
            "Announcement": 'injectable'
        }
        message_type = self.context['request'].data['message_type']
        delivery_type = message_types.get(message_type)
        in_seven_days = timezone.now() + timedelta(days=7)
        recipient_ids = [receiver_user.id] if receiver_user is not None else None
        delivery_rule = facility_models.ContentDeliveryRule.find(delivery_type=delivery_type,
                                                                 start=timezone.now(), end=in_seven_days,
                                                                 recipient_ids=recipient_ids, )
        validated_data['delivery_rule'] = delivery_rule

        validated_data['is_response_expected'] = self.context['request'].data['request_reply']

        instance = super(FacilityMessageSerializer, self).create(validated_data)

        # todo sending the pusher message here instead of _create_message() fn usage?

        return instance     # type: Message


class AdminAppSeniorListSerializer(facility_mixins.DeviceStatusSerializerMixin,
                                   facility_mixins.MessageThreadUrlSerializerMixin,
                                   facility_mixins.ProfilePictureUrlSerializerMixin,
                                   serializers.ModelSerializer, ):
    # todo: How this serializer compares to alexa.SeniorSerializer?
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no',
                  'device_status',
                  'message_thread_url',
                  'profile_picture_url', )

    device_status = serializers.SerializerMethodField()
    message_thread_url = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.MessageResponse
        fields = ('id', 'created', 'content')

    content = serializers.SerializerMethodField()

    @staticmethod
    def get_content(message_response: facility_models.MessageResponse):
        response_types = {
            True: 'Yes',
            False: 'No',
            None: 'No Reply Yet'
        }
        return response_types.get(message_response.response)


class FacilityStaffSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'user_type', 'senior_living_facility')


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'time', 'message_type', 'message_from', 'content', 'reply')

    time = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    message_type = serializers.SerializerMethodField()
    message_from = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()

    @staticmethod
    def get_time(message: Message):
        return message.created

    @staticmethod
    def get_content(message: Message):
        assert message.audio_file or message.content, (
            "For Message instance either audio_file or content is supposed to be set. "
            "It is not so for ID: {}".format(message.id)
        )

        content_type, content_details = ('Audio', message.audio_file.url, ) if message.content is None \
            else ('Text', message.content, )

        return {
            "type": content_type,
            "details": content_details
        }

    @staticmethod
    def get_message_type(message: Message):
        message_types = {
            ContentDeliveryRule.TYPE_VOICE_MAIL: 'Message',
            ContentDeliveryRule.TYPE_URGENT_MAIL: 'Broadcast',
            ContentDeliveryRule.TYPE_INJECTABLE: 'Announcement'
        }
        return message_types.get(message.delivery_rule.type)

    @staticmethod
    def get_message_from(message: Message):
        return FacilityStaffSerializer(message.source_user).data

    @staticmethod
    def get_reply(message: Message):
        if not message.is_response_expected:
            return None
        message_response = facility_models.MessageResponse.objects.filter(message=message)
        if message_response.count() == 0:
            return 'No Reply Yet'
        return ResponseSerializer(message_response).data


class MessageThreadParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.MessageThreadParticipant
        fields = ('id', 'resident', 'last_message', )

    resident = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    @staticmethod
    def get_resident(message_thread_participant: facility_models.MessageThreadParticipant):
        if not message_thread_participant.user:
            return {
                'All Residents': True,
                'message-thread-url': reverse('message-thread', kwargs={'pk': message_thread_participant.id})
            }
        return AdminAppSeniorListSerializer(message_thread_participant.user).data

    @staticmethod
    def get_last_message(message_thread_participant: facility_models.MessageThreadParticipant):
        last_message = message_thread_participant.message_thread.last_message
        return MessageSerializer(last_message).data

class MorningCheckInDoneByStaffSerializer(facility_mixins.MorningCheckInSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no', ) + facility_mixins.MorningCheckInSerializerMixin.get_check_in_fields()

    device_status = serializers.SerializerMethodField()
    check_in_info = serializers.SerializerMethodField(method_name='get_info_for_checked_in')
    message_thread_url = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()


class MorningCheckInDoneByUserSerializer(facility_mixins.MorningCheckInSerializerMixin, serializers.ModelSerializer):
    """
    todo this serializer cannot provide URL for reversing check in! Or can it?!
    """
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no', ) + facility_mixins.MorningCheckInSerializerMixin.get_base_fields()

    device_status = serializers.SerializerMethodField()
    message_thread_url = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()


class MorningCheckInNotDoneSerializer(facility_mixins.MorningCheckInSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'last_name',
                  'room_no', ) + facility_mixins.MorningCheckInSerializerMixin.get_check_in_fields()

    device_status = serializers.SerializerMethodField()
    check_in_info = serializers.SerializerMethodField(method_name='get_info_for_not_checked_in')
    message_thread_url = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()


class MessageThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageThread
        fields = ('pk', 'resident', 'messages')

    messages = serializers.SerializerMethodField()
    resident = serializers.SerializerMethodField()

    @staticmethod
    def get_resident(message_thread: MessageThread):
        resident = message_thread.resident_participant
        return AdminAppSeniorListSerializer(resident).data if isinstance(resident, User) else resident

    @staticmethod
    def get_messages(message_thread: MessageThread):
        return {
            'url': reverse('message-thread-messages', kwargs={'pk': message_thread.id})
        }


class SeniorDeviceUserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.SeniorDeviceUserActivityLog
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
        model = facility_models.SeniorLivingFacilityContent
        fields = ('hash', 'audio_url', 'delivery_rule', )

    hash = serializers.SerializerMethodField()
    delivery_rule = ContentDeliveryRuleSerializer()

    @staticmethod
    def get_hash(content: facility_models.SeniorLivingFacilityContent):
        return content.hash


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


class PhotoGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.Photo
        fields = ('day', )

    day = serializers.SerializerMethodField()

    @staticmethod
    def get_day(photo: facility_models.Photo):
        photo_url = reverse('photo-day-view', kwargs={'pk': photo.photo_gallery_id, 'date': photo.date.isoformat()})
        return {
            'date': photo.date.isoformat(),
            'url': photo_url
        }


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = facility_models.Photo
        fields = ('id', 'url', )
