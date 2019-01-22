from rest_framework import serializers
from alexa.models import AUserMedicalState, Joke, News, User, FamilyProspect
from actions.models import UserAction
from actions.api.serializers import ActionSerializer
from actstream.models import action_object_stream
from random import randint
from django.core.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type', )


class FamilyMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', )

    phone_number = serializers.SerializerMethodField()

    def get_phone_number(self, user: User):
        return user.phone_number.as_national


class FamilyProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyProspect
        fields = ('pk', 'first_name', 'last_name', 'email', 'user_type', 'phone_number', )

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


class SeniorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'last_name', 'room_no', 'primary_contact', )

    primary_contact = serializers.SerializerMethodField()

    def get_primary_contact(self, senior: User):
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
                                                                                randint(0,1000000))

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
                from rest_framework.serializers import ValidationError as RestFrameworkValidationError
                raise RestFrameworkValidationError(detail={'errors': e.messages})

            fp.save()

        return senior


class MedicalStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AUserMedicalState
        fields = ('user', 'measurement', 'data', 'created', )

    data = serializers.JSONField()


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
