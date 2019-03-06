from rest_framework import serializers
from alexa.models import Joke, News, User, FamilyProspect, Circle, UserSettings
from actions.models import UserAction
from senior_living_facility.models import SeniorDeviceUserActivityLog
from streaming.models import Tag
from actions.api.serializers import ActionSerializer
from actstream.models import action_object_stream
from random import randint
from django.core.exceptions import ValidationError
from rest_framework.serializers import ValidationError as RestFrameworkValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type', 'senior_living_facility', 'profile_pic_url', 'senior', )

    profile_pic_url = serializers.SerializerMethodField()
    senior = serializers.SerializerMethodField()

    def get_profile_pic_url(self, user: User):
        return user.get_profile_pic()

    def get_senior(self, user: User):
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
        fields = ('pk', 'members', 'senior')

    senior = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    def get_members(self, circle: Circle):
        return UserSerializer(circle.members, many=True).data

    def get_senior(self, circle: Circle):
        return SeniorSerializer(circle.person_of_interest).data


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


class SeniorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'room_no', 'primary_contact', 'device_status', )

    primary_contact = serializers.SerializerMethodField()
    device_status = serializers.SerializerMethodField()

    @staticmethod
    def get_primary_contact(senior: User):
        circle = senior.circle_set.all()[0]
        admins = circle.admins
        if admins.count() == 0:
            prospects = FamilyProspect.objects.filter(senior=senior).all()
            return FamilyProspectSerializer(prospects[0]).data if prospects.count() > 0 else None
        return FamilyMemberSerializer(admins[0]).data if admins.count() else None

    @staticmethod
    def get_device_status(senior: User):
        device = senior.device

        if not device:
            return None

        last_user_log = SeniorDeviceUserActivityLog.get_last_user_log(senior)

        if not last_user_log:
            last_activity_time = None
            is_today_checked_in = False
        else:
            facility = senior.senior_living_facility
            last_activity_time = last_user_log.created
            is_today_checked_in = last_user_log.is_activity_counted_as_check_in(facility)

        return {
            'is_online': device.is_online,
            'status_checked': device.status_checked,
            'last_activity_time': last_activity_time,
            'is_today_checked_in': is_today_checked_in,
        }

    def create(self, validated_data):
        facility_admin = self.context['request'].user   # type: User

        validated_data['senior_living_facility'] = facility_admin.senior_living_facility
        validated_data['user_type'] = User.CARETAKER
        validated_data['email'] = 'admin_created_{}_{}@proxy.caressa.ai'.format(facility_admin.senior_living_facility.facility_id,
                                                                                randint(0,1000000))
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

        if not any([contact_name, contact_email, contact_phone_number]):    # no family propect earlier, all contact fields are empty
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


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('id',
                  'headline',
                  'content',
                  'user_actions', )

    user_actions = serializers.SerializerMethodField()

    def get_user_actions(self, news: News):
        """
        This is the actions on the News object from the user in the request.

        :param news:
        :return:
        """

        user = self.context['request'].user
        actions = action_object_stream(news).filter(actor_object_id=user.id)
        user_actions = UserAction.objects.all().filter(id__in=[action.id for action in actions])
        return ActionSerializer(user_actions, many=True, context={'request': self.context['request']}).data
