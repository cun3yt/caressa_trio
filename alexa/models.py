from caressa.settings import ENV as SETTINGS_ENV
from django.contrib.auth.models import BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from jsonfield import JSONField
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from django.apps import apps
from utilities.logger import log
from django.db.models import signals
from actstream import action
from actstream.actions import follow as act_follow
from actstream.models import Action
from caressa.settings import pusher_client
from alexa.mixins import FetchRandomMixin
from rest_framework.renderers import JSONRenderer
from caressa.settings import HOSTED_ENV
from django.utils import timezone
from random import sample
from senior_living_facility.models import SeniorLivingFacility
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from uuid import uuid4
from django.urls import reverse
from caressa.settings import WEB_BASE_URL, S3_PRODUCTION_BUCKET, S3_REGION
from utilities.email import send_email
from utilities.sms import send_sms
from typing import Union


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
        user.is_superuser = True
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
    is_anonymous_user = models.BooleanField(default=True,
                                            help_text='Having this field anonymous means that the content will '
                                                      'not be optimized on the personal level, e.g. calling by '
                                                      'name. Once you set the user\'s first name properly you can '
                                                      'set this field to `False`', )

    objects = CaressaUserManager()

    def get_profile_picture_url(self, dimensions, file_format):
        upper_dir = self.id if self.profile_pic else 'no_user'
        profile_picture = self.profile_pic if self.profile_pic else 'default_profile_pic'
        return '{region}/{bucket}/images/user/{upper_dir}/{profile_picture}_{dimensions}.{file_format}'.format(region=S3_REGION,
                                                                                                               bucket=S3_PRODUCTION_BUCKET,
                                                                                                               profile_picture=profile_picture,
                                                                                                               upper_dir=upper_dir,
                                                                                                               dimensions=dimensions,
                                                                                                               file_format=file_format)

    def get_profile_pic(self):
        return self.get_profile_picture_url('w_250', 'jpg')

    def get_profile_pictures(self):
        return {
            'w_250': self.get_profile_picture_url('w_250', 'jpg'),
            'w_25': self.get_profile_picture_url('w_25', 'jpg'),
            'raw': self.get_profile_picture_url('raw', 'png'),
        }

    def is_senior(self):
        return self.user_type == self.CARETAKER

    def is_family(self):
        return self.user_type == self.FAMILY

    def is_provider(self):
        return self.user_type in (self.CAREGIVER, self.CAREGIVER_ORG)

    @property
    def senior_circle(self) -> Union['Circle', None]:
        if self.user_type not in (self.CARETAKER, self.FAMILY, ):
            raise KeyError("User type expected to be {user_type}. Found: {found_type}".format(user_type=self.CARETAKER,
                                                                                              found_type=self.user_type))

        if self.circle_set.all().count() == 0:
            return None

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

    @classmethod
    def get_family_circle_channel(cls, circle_id):
        return 'channel.family.circle.{circle_id}'.format(circle_id=circle_id)

    @classmethod
    def get_facility_channel(cls, facility_id):
        return 'channel.slf.{facility_id}'.format(facility_id=facility_id)

    @property
    def senior_communication_channel(self):  # todo: combine with `self.communication_channels` since serving for the same purpose
        assert self.user_type == self.CARETAKER, (
            "pusher_channel is only available for user_type: senior. "
            "It is {user_type} for user.id: {user_id}".format(user_type=self.user_type,
                                                              user_id=self.id)
        )
        return self.get_family_circle_channel(circle_id=self.senior_circle.id)

    def communication_channels(self):
        if self.is_senior():
            circle_channel = self.get_family_circle_channel(circle_id=self.senior_circle.id)
            slf_channel = self.get_facility_channel(facility_id=self.senior_living_facility.facility_id)
            return [circle_channel, slf_channel, ]

        if self.is_family():
            circle = self.circle_set.all()[0]       # todo better unified with `senior_circle` somehow
            circle_channel = self.get_family_circle_channel(circle_id=circle.id)
            return [circle_channel, ]

        assert self.is_provider(), (
            "For the code to reach the end point the only possibility is user's being provider"
        )

        slf_channel = self.get_facility_channel(facility_id=self.senior_living_facility.facility_id)
        return [slf_channel, ]

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

    def is_admin(self, member: User):
        return self.is_member(member) and member in self.admins

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

    def __repr__(self):     # pragma: no cover
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
            raise ValidationError('At least email address or phone number must be provided for family member')

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

        outreach = FamilyOutreach(prospect=self)

        if self.email:
            outreach.method = FamilyOutreach.TYPE_EMAIL
            outreach.data = {
                'type': 'email',
                'status': 'attempted'
            }
            outreach.save()

            send_res, html_content, text_content, to_email_address = \
                send_email([self.email],
                           'Invitation from {}'.format(self.senior.senior_living_facility),
                           'email/reach-prospect.html',
                           'email/reach-prospect.txt',
                           context={
                               'prospect': self,
                               'facility': self.senior.senior_living_facility,
                               'invitation_url': outreach.invitation_url,
                           })

            outreach.data.update({
                'status': 'sent',
                'send_result': send_res,
                'html_content': html_content,
                'text_content': text_content,
                'to_email_address': to_email_address
            })
            outreach.save()

        elif self.phone_number:
            outreach.method = FamilyOutreach.TYPE_TEXT
            outreach.data = {
                'type': 'text',
                'status': 'attempted'
            }
            outreach.save()

            to_phone_number = str(self.phone_number)

            send_res, text_content, to_phone_number = send_sms(
                to_phone_number=to_phone_number,
                template_txt='email/reach-prospect.txt',
                context={
                    'prospect': self,
                    'facility': self.senior.senior_living_facility,
                    'prospect_senior_full_name': self.senior.full_name,
                    'invitation_url': outreach.invitation_url
                }
            )

            outreach.data.update({
                'status': 'sent',
                'send_result': send_res,
                'text_content': text_content,
                'to_phone_number': to_phone_number
            })
            outreach.save()

        return True


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


class UserSettings(TimeStampedModel):
    class Meta:
        db_table = 'user_settings'

    # For a new user settings type, add the default value to be back filled for all users.
    # If there is new field in data is needed, add entry to DEFAULTS dictionary and getter/setter methods
    DEFAULTS = {
        'genres': []
    }

    user = models.ForeignKey(to=User,
                             null=False,
                             on_delete=models.DO_NOTHING,
                             related_name='settings', )
    data = JSONField(default=DEFAULTS)  # payload info: e.g. which genres selected.

    @property
    def genres(self):
        return self.data.get('genres', self.DEFAULTS['genres'])

    @genres.setter
    def genres(self, genres):
        self.data['genres'] = genres


class CircleInvitation(TimeStampedModel):
    class Meta:
        db_table = 'circle_invitation'

    circle = models.ForeignKey(to=Circle, on_delete=models.DO_NOTHING, null=False, )
    email = models.EmailField(_('email address'), null=False, unique=True, )
    inviter = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, related_name='circle_inviter')
    name = models.TextField(null=True, )
    surname = models.TextField(null=True, )
    invitation_code = models.UUIDField(default=uuid4, db_index=True, )
    converted_user = models.ForeignKey(to=User,
                                       on_delete=models.DO_NOTHING,
                                       null=True,
                                       related_name='created_user_from_invitation')

    @property
    def invitation_url(self):
        return '{base_url}{url}?invitation_code={code}'.format(base_url=WEB_BASE_URL,
                                                               url=reverse('circle-member-invitation'),
                                                               code=self.invitation_code)

    def send_circle_invitation_mail(self) -> bool:
        send_email([self.email],
                   'Invitation from {}'.format(self.inviter.first_name),
                   'email/circle-invitation.html',
                   'email/circle-invitation.txt',
                   context={
                       'invitation': self,
                       'inviter': self.inviter,
                       'invitation_url': self.invitation_url,
                   })
        return True


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

    def __str__(self):  # pragma: no cover
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


def create_circle_for_user(sender, instance, created, **kwargs):
    user = instance     # type: User
    if user.user_type is not User.CARETAKER:
        return
    user.create_initial_circle()


signals.post_save.connect(receiver=create_circle_for_user, sender=User, dispatch_uid='create_circle_for_user')
signals.post_save.connect(user_act_on_content_activity_save, sender=UserActOnContent)
