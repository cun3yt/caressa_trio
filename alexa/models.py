from caressa.settings import ENV as SETTINGS_ENV
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from jsonfield import JSONField
from model_utils.models import TimeStampedModel, StatusField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField
from django.apps import apps
from utilities.dictionaries import deep_get, deep_set
from utilities.logger import log
from django.db.models import signals
from actstream import action
from actstream.actions import follow as act_follow
from actstream.models import Action
from caressa.settings import pusher_client
from alexa.mixins import FetchRandomMixin
from rest_framework.renderers import JSONRenderer
from caressa.settings import CONVERSATION_ENGINES, HOSTED_ENV
from datetime import timedelta, datetime
from django.utils import timezone
from random import sample
from icalendar import Calendar
from django.utils.crypto import get_random_string
from caressa.hardcodings import HC_HARDWARE_USER_DEVICE_ID_PREFIX
from senior_living_facility.models import SeniorLivingFacility
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from uuid import uuid4
from django.urls import reverse
from caressa.settings import WEB_BASE_URL
from utilities.email import send_email


class CaressaUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class AbstractCaressaUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=False, null=False, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CaressaUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True
        db_table = 'user'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractCaressaUser, TimeStampedModel):
    CARETAKER = 'SENIOR'
    FAMILY = 'FAMILY'
    CAREGIVER = 'CAREGIVER'
    CAREGIVER_ORG = 'CAREGIVER_ORG'

    TYPE_SET = (
        (CARETAKER, 'Senior'),
        (FAMILY, 'Family Member'),
        (CAREGIVER, 'Caregiver'),
        (CAREGIVER_ORG, 'Caregiver Organization'),
    )

    user_type = models.TextField(
        choices=TYPE_SET,
        default=CARETAKER,
    )

    phone_number = PhoneNumberField(db_index=True, blank=True)
    profile_pic = models.TextField(blank=True, default='')
    state = models.TextField(blank=False, default='unknown')
    city = models.TextField(blank=False, default='unknown')
    senior_living_facility = models.ForeignKey(to=SeniorLivingFacility, on_delete=models.DO_NOTHING, null=True, )
    room_no = models.CharField(verbose_name="Room Number",
                               max_length=8,
                               null=False,
                               default='',
                               blank=True,
                               help_text="The room number of the senior. It is only meaningful for the senior", )
    hardware = models.ForeignKey(to='streaming.HardwareRegistry',
                                 null=True,
                                 default=None,
                                 help_text="The hardware in senior's room",
                                 on_delete=models.DO_NOTHING, )
    is_anonymous_user = models.BooleanField(default=True,
                                            help_text='Having this field anonymous means that the content will '
                                                      'not be optimized on the personal level, e.g. calling by '
                                                      'name. Once you set the user\'s first name properly you can '
                                                      'set this field to `False`', )

    objects = CaressaUserManager()

    def get_profile_pic(self):
        return '/statics/{}.png'.format(self.profile_pic) if self.profile_pic else None

    def is_senior(self):
        return self.user_type == self.CARETAKER

    def is_family(self):
        return self.user_type == self.FAMILY

    def is_provider(self):
        return self.user_type in (self.CAREGIVER, self.CAREGIVER_ORG)

    @property
    def senior_circle(self) -> 'Circle':
        if self.user_type != self.CARETAKER:
            raise KeyError("User type expected to be {user_type}. Found: {found_type}".format(user_type=self.CARETAKER,
                                                                                              found_type=self.user_type))
        return self.circle_set.all()[0]

    @property
    def full_name(self):
        return self.get_full_name()

    def create_initial_circle(self):
        membership = CircleMembership.objects.filter(member_id=self.id)
        if membership.count() > 0:
            return False
        circle = Circle(person_of_interest=self)
        circle.save()
        circle_member = User.objects.get(id=self.id)
        circle.add_member(circle_member, False)
        return True

    @property
    def pusher_channel(self):
        assert self.user_type == self.CARETAKER, (
            "pusher_channel is only available for user_type: senior. "
            "It is {user_type} for user.id: {user_id}".format(user_type=self.user_user_type,
                                                              user_id=self.id)
        )
        return 'family.senior.{id}'.format(id=self.id)

    @staticmethod
    def create_test_user():
        test_user = User(password=get_random_string(),
                         first_name='AnonymousFirstName',
                         last_name='AnonymousLastName',
                         is_staff=False,
                         is_superuser=False,
                         email='test{}@caressa.ai'.format(get_random_string(15)),
                         phone_number='+14153477898',
                         profile_pic='default_profile_pic',
                         state='test_state',
                         city='test_city', )
        return test_user

    def __repr__(self):
        return self.first_name.title()

    def __str__(self):
        return self.get_full_name()


class Circle(TimeStampedModel):
    class Meta:
        db_table = 'circle'

    members = models.ManyToManyField(User, through='CircleMembership', through_fields=('circle', 'member', ), )
    person_of_interest = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=False, related_name='main_circle')

    def __repr__(self):
        circle_owner = self.person_of_interest
        member_count = self.members.count()
        return 'Circle of [{circle_owner}] with {count} member(s)'.format(circle_owner=circle_owner,
                                                                          count=member_count)

    def add_member(self, member: User, is_admin: bool):
        CircleMembership.add_member(self, member=member, is_admin=is_admin)

    def is_member(self, member: User):
        return CircleMembership.is_member(self, member)

    @property
    def admins(self):
        return self.members.filter(circle_memberships__is_admin=True).all()


class CircleMembership(TimeStampedModel):
    class Meta:
        db_table = 'circle_membership'
        unique_together = ('circle', 'member', )

    circle = models.ForeignKey(Circle, on_delete=models.DO_NOTHING, related_name='circle')
    member = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='circle_memberships')
    is_admin = models.BooleanField(default=False)

    @classmethod
    def add_member(cls, circle: Circle, member: User, is_admin: bool) -> None:
        if cls.objects.filter(circle=circle, member=member).count() > 0:
            log("{member} is already a member of circle: {circle}\n"\
                "Other parameters are ignored even if "\
                "they are different from the current object".format(member=member, circle=circle))
            return
        cls.objects.create(circle=circle, member=member, is_admin=is_admin)

        # Setting follows relationship from the circle POI to the added member
        act_follow(circle.person_of_interest, member, send_action=False, actor_only=False)
        action.send(member, verb='joined the circle')

    @classmethod
    def is_member(cls, circle: Circle, member: User) -> bool:
        return cls.objects.filter(circle=circle, member=member).count() > 0

    def __repr__(self):
        return 'CircleMembership ({id}): {member} in {circle} with admin: {admin} and POI: {poi}'\
            .format(id=self.id, member=self.member, circle=self.circle, admin=self.is_admin,
                    poi=(self.circle.person_of_interest == self.member))


class FamilyProspect(TimeStampedModel):
    class Meta:
        db_table = 'family_prospect'

    name = models.TextField(blank=False)
    email = models.EmailField(blank=True, default='')
    phone_number = PhoneNumberField(blank=True, default='')
    senior = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)

    def clean(self):
        if (not self.email) and (not self.phone_number):
            raise ValidationError('Either email or phone_number must be provided for family member entry')

    def send_email(self, address, template_name, context):
        raise NotImplementedError   # todo Implement

    def send_text(self, phone_number, template_name, context):
        raise NotImplementedError   # todo Implement

    def reach_prospect(self) -> bool:
        try:
            circle = self.senior.senior_circle
        except KeyError as e:
            log(str(e) + ' >> Function returning false')
            return False

        if circle.admins.count() > 0:
            return False

        # Assumption: FamilyOutreach is assumed to be successful outreach
        family_outreach_qs = FamilyOutreach.objects.filter(prospect=self)

        if family_outreach_qs.count() > 0:
            return False

        outreach = FamilyOutreach(prospect=self)    # todo check if tracking_code exists here (without save)

        if self.email:
            outreach.method = FamilyOutreach.TYPE_EMAIL
            outreach.data = {
                'email_address': self.email,
                'email_template': 'tbd.html'     # todo: to be filled
            }
            outreach.save()

            send_email(self.email,
                       'Invitation from {}'.format(self.senior.senior_living_facility),
                       'email/reach-prospect.html',
                       'email/reach-prospect.txt',
                       context={
                           'prospect': self,
                           'facility': self.senior.senior_living_facility,
                           'invitation_url': outreach.invitation_url,
                       })

        elif self.phone_number:
            raise NotImplementedError
            # outreach.method = FamilyOutreach.TYPE_TEXT
            # outreach.data = {
            #     'phone_number': self.phone_number,
            #     'text_content': 'tbd.html'  # todo: to be filled
            # }
            # outreach.save()
            # self.send_text(self.phone_number,
            #                outreach.data['text_content'],
            #                context={
            #                    'tracking_code': outreach.tracking_code,
            #                    'senior': self.senior,
            #                    'prospect': self
            #                })


class FamilyOutreach(TimeStampedModel):
    class Meta:
        db_table = 'family_outreach'

    TYPE_EMAIL = 'email'
    TYPE_TEXT = 'text'

    TYPE_SET = (
        (TYPE_EMAIL, 'email'),
        (TYPE_TEXT, 'text'),
    )

    prospect = models.ForeignKey(to=FamilyProspect, null=True, on_delete=models.DO_NOTHING, )
    method = models.TextField(choices=TYPE_SET,
                              null=False, )
    data = JSONField(default={})    # payload info: e.g. what email address
    # todo success/failure state?
    tracking_code = models.UUIDField(default=uuid4, db_index=True)
    converted_user = models.ForeignKey(to=User, null=True, default=None, on_delete=models.DO_NOTHING, )

    @property
    def invitation_url(self):
        return '{base_url}{url}?invitation_code={code}'.format(base_url=WEB_BASE_URL,
                                                               url=reverse('family-prospect-invitation-code'),
                                                               code=self.tracking_code)


class AUser(TimeStampedModel):
    class Meta:
        db_table = 'a_user'
        indexes = [
            models.Index(fields=['alexa_device_id', 'alexa_user_id'])
        ]

    alexa_user_id = models.TextField(editable=False)
    alexa_device_id = models.TextField(editable=False)
    user = models.ForeignKey(to=User, null=True, on_delete=models.DO_NOTHING, related_name='a_users')
    engine_schedule = models.TextField(null=False, blank=True, default="")
    profile = JSONField(default={})

    def last_engine_session(self, state=None) -> 'EngineSession':
        if not state:
            return self.engine_sessions.order_by('modified').last()
        return self.engine_sessions.filter(state=state).order_by('modified').last()

    def set_emotion(self, emotion, value):
        state = AUserEmotionalState(user=self, attribute=emotion, value=value)
        state.save()
        return state

    def update_emotion(self, emotion, increment=None, percentage=None, max_value=100, min_value=0):
        state = self.emotional_states.filter(attribute=emotion).last()
        value = float(state.value if state else AUserEmotionalState.EMOTION_DEFAULTS[emotion])

        if increment and 0 <= increment:
            new_value = value + increment
            new_value = new_value if new_value < max_value else max_value
        elif increment and increment < 0:
            new_value = value + increment
            new_value = new_value if min_value < new_value else min_value
        elif percentage and 0 <= percentage:
            new_value = value * (1+percentage/100)
            new_value = new_value if new_value < max_value else max_value
        elif percentage and percentage < 0:
            new_value = value * (1+percentage/100)
            new_value = new_value if min_value < new_value else min_value
        else:
            raise Exception("Problem with increment/percentage in emotion value update")

        new_state = AUserEmotionalState(user=self, attribute=emotion, value=new_value)
        new_state.save()
        return new_state

    def set_medical_state(self, measurement, data):
        state = AUserMedicalState(user=self, measurement=measurement, data=data)
        state.save()
        return state

    def profile_get(self, key):
        return deep_get(self.profile, key, None)

    def profile_set(self, key, value):
        deep_set(self.profile, key, value)
        self.save()

    def create_initial_engine_scheduler(self):
        if not self.engine_schedule == '':
            return False
        auser_id = self.id
        user = AUser.objects.get(id=auser_id)
        cal = Calendar()
        cal.add('dtstart', datetime.now())
        cal.add('summary', 'schedule of user:{}'.format(auser_id))

        user.engine_schedule = cal.to_ical().decode(encoding='UTF-8')
        user.save()
        return True

    def is_hardware_user(self) -> bool:
        prefix = HC_HARDWARE_USER_DEVICE_ID_PREFIX
        return self.alexa_device_id.startswith(prefix)

    @staticmethod
    def get_or_create_by(alexa_device_id, alexa_user_id):
        """
        For given device ID and user ID, it creates and saves an AUser instance if not found.
        If alexa user is created, it also creates a User instance and saves it as a side effect.

        :param alexa_device_id: string
        :param alexa_user_id: int
        :return: (AUser, bool)
        """

        alexa_user, is_created = AUser.objects.get_or_create(alexa_device_id=alexa_device_id,
                                                             alexa_user_id=alexa_user_id, )

        if is_created:
            test_user = User.create_test_user()
            test_user.save()
            alexa_user.user = test_user
            alexa_user.save()

        return alexa_user, is_created


class AUserEmotionalState(TimeStampedModel):
    class Meta:
        db_table = 'a_user_emotional_state'
        ordering = ('-created',)

    EMOTIONS = Choices('happiness', 'anxiety', 'delusional', 'loneliness')
    EMOTION_DEFAULTS = {
        'happiness': 50.0,
        'anxiety': 50.0,
        'delusional': 50.0,
        'loneliness': 50.0,
    }

    user = models.ForeignKey(to=AUser, null=False, related_name='emotional_states', on_delete=models.DO_NOTHING)
    attribute = StatusField(choices_name='EMOTIONS', db_index=True)
    value = models.DecimalField(max_digits=5, decimal_places=2)


AUserEmotionalState._meta.get_field('created').db_index = True


class AUserMedicalState(TimeStampedModel):
    class Meta:
        db_table = 'a_user_medical_state'

    MEASUREMENTS = Choices('blood_pressure')

    user = models.ForeignKey(to=AUser, null=False, related_name='medical_state', on_delete=models.DO_NOTHING)
    measurement = StatusField(choices_name='MEASUREMENTS', db_index=True)
    data = JSONField(default={})


AUserMedicalState._meta.get_field('created').db_index = True


class Request(TimeStampedModel):
    class Meta:
        db_table = 'a_request'

    user = models.ForeignKey(AUser, null=False, related_name='requests', on_delete=models.DO_NOTHING)
    handler_engine = models.TextField(blank=True, null=False, default='')


Request._meta.get_field('created').db_index = True


class Session(TimeStampedModel):
    class Meta:
        db_table = 'a_session'

    alexa_id = models.TextField(db_index=True, editable=False)
    alexa_user = models.ForeignKey(to='AUser', on_delete=models.CASCADE, related_name='sessions')


Session._meta.get_field('created').db_index = True


class EngineSession(TimeStampedModel):
    class Meta:
        db_table = 'a_engine_session'

    user = models.ForeignKey(AUser, null=False, related_name='engine_sessions', on_delete=models.DO_NOTHING)
    name = models.TextField(null=False, blank=False)
    state = models.TextField(blank=True, db_index=True)
    # Possible `state`s: continue, done, expired
    data = JSONField(default={})
    ttl = models.PositiveIntegerField(default=CONVERSATION_ENGINES['ttl'])

    @property
    def is_continuing(self):
        self._expire_if_ttl_past()
        return self.state == 'continue'

    @property
    def is_ttl_past(self):
        return (self.modified + timedelta(seconds=self.ttl)) < timezone.now()

    def _expire_if_ttl_past(self):
        if self.state != 'continue':
            return
        if self.is_ttl_past:
            self.state = 'expired'
            self.save()

    def set_state_continue(self, additional_level=None, start_level=None, asked_question=None):
        self._set_state('continue',
                        additional_level=additional_level,
                        start_level=start_level,
                        asked_question=asked_question)

    def set_state_done(self, additional_level=None, start_level=None, asked_question=None):
        self._set_state('done',
                        additional_level=additional_level,
                        start_level=start_level,
                        asked_question=asked_question)

    def set_target_object_id(self, id):
        self.data['target_object_id'] = id

    def get_target_object_id(self):
        return self.data.get('target_object_id', None)

    def set_data(self, key, value):     # todo make other related functions use this one
        self.data[key] = value

    def get_data(self, key):    # todo make other related functions use this one
        return self.data.get(key, None)

    def _add_asked_question(self, question):
        self.data['asked_questions'].append(question)

    def _set_state(self, state, additional_level=None, start_level=None, asked_question=None):
        if additional_level is not None:
            self._add_level(additional_level)
        elif start_level is not None:
            self._set_level(start_level)

        if asked_question is not None:
            self._add_asked_question(asked_question)

        self.state = state

    def _set_level(self, level):
        self.data['level'] = level

    def _add_level(self, additional_level):
        self.data['level'] = '{current_level}.{additional_level}'.format(current_level=self.data['level'],
                                                                         additional_level=additional_level)


Request._meta.get_field('created').db_index = True
Request._meta.get_field('modified').db_index = True


class Joke(TimeStampedModel, FetchRandomMixin):
    class Meta:
        db_table = 'joke'

    main = models.TextField(null=False, blank=False)
    punchline = models.TextField(null=False, blank=False)

    def __repr__(self):
        return "Joke({id}, {main}-{punchline})".format(id=self.id,
                                                       main=self.main,
                                                       punchline=self.punchline)

    def __str__(self):
        return "a joke"


class News(TimeStampedModel, FetchRandomMixin):
    class Meta:
        db_table = 'news'

    headline = models.TextField(null=False, blank=False)
    content = models.TextField(null=False, blank=False)

    def __repr__(self):
        return "News({id}, {headline})".format(id=self.id, headline=self.headline)

    def __str__(self):
        return "sample news"


class FactType(TimeStampedModel):
    class Meta:
        db_table = 'fact_type'

    name = models.TextField(null=False,
                            blank=False,
                            db_index=True)

    def __str__(self):
        return "{}".format(self.name)


class Fact(TimeStampedModel, FetchRandomMixin):
    class Meta:
        db_table = 'fact'

    fact_type = models.ForeignKey(db_column='type',
                                  to=FactType,
                                  null=True,
                                  on_delete=models.DO_NOTHING,
                                  related_name='facts')
    entry_text = models.TextField(null=False, blank=False)
    fact_list = JSONField(default=[])
    ending_yes_no_question = models.TextField(null=False, blank=False)

    def get_random_content(self):
        return sample(self.fact_list, 1)[0]

    def __str__(self):
        return "({}) {} - entry text: '{}'".format(self.id,
                                                   self.fact_type.name,
                                                   self.entry_text)


class Song(TimeStampedModel, FetchRandomMixin):
    class Meta:
        db_table = 'song'

    title = models.TextField(null=False, blank=False)
    artist = models.TextField(null=False, blank=False)
    duration = models.PositiveIntegerField(null=False, blank=False)
    genre = models.TextField(null=False, blank=False)
    file_name = models.TextField(null=False, blank=False)

    @property
    def url(self):
        return HOSTED_ENV + self.file_name

    def __repr__(self):
        return "Song({id}, {title} by {artist})".format(id=self.id, title=self.title, artist=self.artist)

    def __str__(self):
        return "test song"


class UserActOnContent(TimeStampedModel):
    class Meta:
        db_table = 'user_act_on_content'

    user = models.ForeignKey(to=User,
                             null=True,
                             on_delete=models.DO_NOTHING,
                             related_name='contents_user_acted_on')
    verb = models.TextField(db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, null=True)
    object_id = models.PositiveIntegerField(null=True)
    object = GenericForeignKey()


def user_act_on_content_activity_save(sender, instance, created, **kwargs):
    from actions.api.serializers import ActionSerializer  # todo move this up
    user_action_model = apps.get_model('actions', 'UserAction')
    user = instance.user
    verb = instance.verb
    action_object = instance.object
    circle = user.circle_set.all()[0]
    action.send(user,
                verb=verb,
                description=kwargs.get('description', ''),
                action_object=action_object,
                target=circle,
                )
    channel_name = 'channel-{env}-circle-{circle}'.format(env=SETTINGS_ENV, circle=circle.id)
    user_action = user_action_model.objects.my_actions(user, circle).order_by('-timestamp')[0]
    serializer = ActionSerializer(user_action)
    json = JSONRenderer().render(serializer.data).decode('utf8')
    pusher_client.trigger(channel_name, 'feeds', json)


def set_init_engine_scheduler_for_auser(sender, instance, created, **kwargs):
    auser = instance    # type: AUser
    auser.create_initial_engine_scheduler()


def create_circle_for_user(sender, instance, created, **kwargs):
    user = instance     # type: User
    user.create_initial_circle()


signals.post_save.connect(receiver=create_circle_for_user, sender=User, dispatch_uid='create_circle_for_user')
signals.post_save.connect(receiver=set_init_engine_scheduler_for_auser, sender=AUser,
                          dispatch_uid='set_init_engine_scheduler_for_auser')
signals.post_save.connect(user_act_on_content_activity_save, sender=UserActOnContent)
