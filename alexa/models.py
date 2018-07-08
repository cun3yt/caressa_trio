from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from jsonfield import JSONField
from model_utils.models import TimeStampedModel, StatusField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

from utilities.dictionaries import deep_get, deep_set
from utilities.logger import log
from django.db.models import signals
from actstream import action
from actstream.actions import follow as act_follow
from actstream.models import Action

from django.contrib.contenttypes.models import ContentType
from alexa.mixins import FetchRandomMixin
from caressa.settings import CONVERSATION_ENGINES
from datetime import timedelta
from django.utils import timezone


class User(AbstractUser, TimeStampedModel):
    class Meta:
        db_table = 'user'

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

    def get_profile_pic(self):
        return '/statics/{}.png'.format(self.profile_pic) if self.profile_pic else None

    def is_senior(self):
        return self.user_type == self.CARETAKER

    def is_family(self):
        return self.user_type == self.FAMILY

    def is_provider(self):
        return self.user_type in (self.CAREGIVER, self.CAREGIVER_ORG)

    def __repr__(self):
        return self.first_name.title()

    def __str__(self):
        return self.first_name.title()


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


class AUser(TimeStampedModel):
    class Meta:
        db_table = 'a_user'

    alexa_id = models.TextField(db_index=True, editable=False)
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
    # Possible `state`s: continue, done (postpone-next-session, postpone-indefinite, expired)
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


class UserActOnContent(TimeStampedModel):
    class Meta:
        db_table = 'user_act_on_content'

    user = models.ForeignKey(to=User,
                             null=True,
                             on_delete=models.DO_NOTHING,
                             related_name='contents_user_acted_on')
    verb = models.TextField(db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    object = GenericForeignKey()


def user_act_on_content_activity_save(sender, instance, created, **kwargs):
    action.send(instance.user,
                verb=instance.verb,
                description=kwargs.get('description', ''),
                action_object=instance.object,
                target=Circle.objects.get(id=1),     # todo: Move to `hard-coding`
                )


signals.post_save.connect(user_act_on_content_activity_save, sender=UserActOnContent)


