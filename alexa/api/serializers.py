from rest_framework import serializers
from alexa.models import Joke, User, FamilyProspect, Circle, UserSettings, CircleInvitation, CircleReinvitation
from actions.models import UserAction
from senior_living_facility.api.mixins import DeviceStatusSerializerMixin, MessageThreadUrlSerializerMixin, \
    ProfilePictureUrlSerializerMixin, MorningCheckInSerializerMixin
from streaming.models import Tag
from actions.api.serializers import ActionSerializer
from actstream.models import action_object_stream
from random import randint
from django.core.exceptions import ValidationError
from rest_framework.serializers import ValidationError as RestFrameworkValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type',
                  'senior_living_facility', 'senior', 'profile_picture_url', 'thumbnail_url', )

    profile_picture_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    senior = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_picture_url(user: User):
        return user.get_profile_pic()

    @staticmethod
    def get_thumbnail_url(user: User):
        return user.get_thumbnail_url()

    @staticmethod
    def get_senior(user: User):
        if not user.user_type == User.FAMILY:
            return {}
        senior = user.senior_circle.person_of_interest
        return {
            'id': senior.id,
            'first_name': senior.first_name,
            'last_name': senior.last_name,
            'profile_pic_url': senior.profile_pic,
        }


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ('pk', 'settings', )

    settings = serializers.SerializerMethodField()

    def get_settings(self, user_settings: UserSettings):
        def _setting_to_item(setting, is_selected):
            return {'label': setting.label, 'id': setting.id, 'is_selected': is_selected}

        available_settings_genres = Tag.objects.all().filter(is_setting_available=True)
        selected_genre_ids = user_settings.genres

        genres_with_user_preference = [_setting_to_item(setting=setting, is_selected=True)
                                       if setting.id in selected_genre_ids
                                       else _setting_to_item(setting=setting, is_selected=False)
                                       for setting in available_settings_genres]
        return {'genres': genres_with_user_preference}

    def update(self, instance: UserSettings, validated_data):
        request = self.context['request']
        genres = request.data.get('settings', {}).get('genres')

        genres_all = [genre['id'] for genre in genres]

        assert len(genres_all) == Tag.objects.filter(pk__in=genres_all, is_setting_available=True).all().count(), (
            "Some of the settings that are intended to be saved are not available!"
        )

        selected_genres = [genre['id'] for genre in genres if genre['is_selected']]

        instance.genres = selected_genres
        instance.save()
        return instance


class CircleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circle
        fields = ('pk', 'members', 'senior', 'pending_invitations')

    senior = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()
    pending_invitations = serializers.SerializerMethodField()

    def get_members(self, circle: Circle):
        members = circle.members.filter(user_type=User.FAMILY)
        members_lst = list(UserSerializer(members, many=True).data)
        admin_ids = [admin.id for admin in circle.admins.all()]

        for index, member in enumerate(members_lst):
            members_lst[index]['is_admin'] = True if member['pk'] in admin_ids else False

        return members_lst

    def get_senior(self, circle: Circle):
        return SeniorSerializer(circle.person_of_interest).data

    def get_pending_invitations(self, circle):
        return CircleInvitationSerializer(circle.pending_invitations, many=True).data


class CircleInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleInvitation
        fields = ('pk', 'created', 'email', 'invitation_code')

    def create(self, validated_data):
        circle_id = self.context['view'].kwargs['circle_pk']
        circle = Circle.objects.get(id=circle_id)
        inviter_user = self.context['request'].user

        circle_invitation = CircleInvitation.objects.create(circle=circle,
                                                            email=validated_data['email'],
                                                            inviter=inviter_user, )

        # todo raise email already exist method mobile friendly.

        circle_invitation.send_circle_invitation_mail()

        return circle_invitation


class CircleReinvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CircleReinvitation
        fields = ('pk', )

    def create(self, validated_data):
        invitation_code = self.context['view'].kwargs['invitation_code']

        circle_invitation = CircleInvitation.objects.get(invitation_code=invitation_code,)
        circle_reinvitation = CircleReinvitation.objects.create(circle_invitation=circle_invitation)
        circle_invitation.send_circle_invitation_mail()

        return circle_reinvitation


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'channels')

    channels = serializers.SerializerMethodField()

    def get_channels(self, user: User):
        return user.communication_channels()


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'is_temporary', )

    is_temporary = serializers.SerializerMethodField()  # Being temporary means that it is editable on form.
    phone_number = serializers.SerializerMethodField()

    def get_phone_number(self, user: User):
        return user.phone_number.as_national if user.phone_number else ''

    def get_is_temporary(self, prospect: FamilyProspect):
        return False


class FamilyProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyProspect
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', 'is_temporary', )

    is_temporary = serializers.SerializerMethodField() # Being temporary means that it is editable on form.
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    def get_first_name(self, prospect: FamilyProspect):
        return prospect.name

    def get_last_name(self, prospect: FamilyProspect):
        return ''

    def get_user_type(self, prospect: FamilyProspect):
        return User.FAMILY

    def get_phone_number(self, prospect: FamilyProspect):
        if not prospect.phone_number:
            return ''
        return prospect.phone_number.as_national

    def get_is_temporary(self, prospect: FamilyProspect):
        return True


class SeniorSerializer(MorningCheckInSerializerMixin,
                       serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'user_type', 'senior_living_facility',
                  'phone_number', 'birth_date', 'move_in_date', 'service_type', 'room_no', 'primary_contact',
                  'caregivers', 'thumbnail_url', ) + MorningCheckInSerializerMixin.get_check_in_fields()

    primary_contact = serializers.SerializerMethodField()
    device_status = serializers.SerializerMethodField()
    caregivers = serializers.SerializerMethodField()
    message_thread_url = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    check_in_info = serializers.SerializerMethodField(method_name='get_info_for_checked_in')

    @staticmethod
    def get_caregivers(senior: User):
        return [{
            "first_name": caregiver.first_name,
            "last_name": caregiver.last_name,
            "phone_number": caregiver.phone_number.as_national if caregiver.phone_number else '',
        } for caregiver in senior.caregivers.all()]

    @staticmethod
    def get_primary_contact(senior: User):
        circle = senior.circle_set.all()[0]
        admins = circle.admins
        if admins.count() == 0:
            prospects = FamilyProspect.objects.filter(senior=senior).all()
            return FamilyProspectSerializer(prospects[0]).data if prospects.count() > 0 else None
        return FamilyMemberSerializer(admins[0]).data if admins.count() else None

    def create(self, validated_data):
        facility_admin = self.context['request'].user   # type: User

        validated_data['senior_living_facility'] = facility_admin.senior_living_facility
        validated_data['user_type'] = User.CARETAKER
        validated_data['email'] = 'admin_created_{}_{}@proxy.caressa.ai'.format(facility_admin.senior_living_facility.facility_id,
                                                                                randint(0, 1000000))
        first_name = validated_data['first_name']

        if not first_name:
            raise RestFrameworkValidationError(detail={'errors': ["Senior's first name is required."]})
        senior = super(SeniorSerializer, self).create(validated_data)

        contact_name = self.context['request'].data.get('contact.name')
        if contact_name:
            contact_email = self.context['request'].data.get('contact.email')
            contact_phone_number = self.context['request'].data.get('contact.phone_number')
            fp = FamilyProspect(name=contact_name,
                                email=contact_email,
                                phone_number=contact_phone_number,
                                senior=senior)

            try:
                fp.full_clean()
            except ValidationError as e:
                raise RestFrameworkValidationError(detail={'errors': e.messages})

            fp.save()

        return senior

    def update(self, instance, validate_data):
        senior = super(SeniorSerializer, self).update(instance, validate_data)

        circle = senior.circle_set.all()[0]
        admins = circle.admins
        if admins.count() > 0:
            return senior

        contact = self.context['request'].data
        contact_name = contact.get('contact.name')
        contact_email = contact.get('contact.email')
        contact_phone_number = contact.get('contact.phone_number')

        if FamilyProspect.objects.filter(senior=senior).count() > 0:    # already there is family prospect
            if not any([contact_name, contact_email, contact_phone_number]):    # all empty
                raise RestFrameworkValidationError(detail={'errors': ['You cannot delete existing contact']})

            if not contact_name:    # deleting name field
                raise RestFrameworkValidationError(detail={'errors': ['You cannot remove existing contact name']})

        # no family prospect earlier, all contact fields are empty
        if not any([contact_name, contact_email, contact_phone_number]):
            return senior

        # This is only created for validation
        fp = FamilyProspect(name=contact_name,
                            email=contact_email,
                            phone_number=contact_phone_number,
                            senior=senior)

        try:
            fp.full_clean()
        except ValidationError as e:
            raise RestFrameworkValidationError(detail={'errors': e.messages})

        FamilyProspect.objects.update_or_create(senior=senior, defaults={
            'name': contact_name,
            'email': contact_email,
            'phone_number': contact_phone_number
        })

        return senior


class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ('id',
                  'main',
                  'punchline',
                  'user_actions', )

    user_actions = serializers.SerializerMethodField()

    def get_user_actions(self, joke: Joke):
        """
        This is the actions on the Joke object from the user in the request.

        :param joke:
        :return:
        """

        user = self.context['request'].user
        actions = action_object_stream(joke).filter(actor_object_id=user.id)
        user_actions = UserAction.objects.all().filter(id__in=[action.id for action in actions])
        return ActionSerializer(user_actions, many=True, context={'request': self.context['request']}).data
