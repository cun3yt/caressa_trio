from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import JSONField
from model_utils.models import TimeStampedModel, StatusField
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField

from utilities.dictionaries import deep_get, deep_set
from random import randint
from stream_django.activity import Activity
from stream_django.feed_manager import feed_manager
from django.db.models import signals


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

    def is_senior(self):
        return self.user_type == self.CARETAKER

    def is_family(self):
        return self.user_type == self.FAMILY

    def is_provider(self):
        return self.user_type in (self.CAREGIVER, self.CAREGIVER_ORG)


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
    state = models.TextField(blank=True)    # continue, done (postpone-next-session, postpone-indefinite, expired)
    data = JSONField(default={})


Request._meta.get_field('created').db_index = True
Request._meta.get_field('modified').db_index = True


class Joke(TimeStampedModel):
    class Meta:
        db_table = 'joke'

    main = models.TextField(null=False, blank=False)
    punchline = models.TextField(null=False, blank=False)

    @staticmethod
    def fetch_random():
        count = Joke.objects.all().count()
        random_slice = randint(0, count-1)
        joke_set = Joke.objects.all()[random_slice: random_slice+1]
        return joke_set[0]


class UserActOnContent(TimeStampedModel, Activity):
    class Meta:
        db_table = 'user_act_on_content'

    user = models.ForeignKey(to=User, null=True, on_delete=models.DO_NOTHING, related_name='contents_user_acted_on')
    verb = models.TextField(db_index=True)
    object = models.ForeignKey(Joke, null=True, on_delete=models.DO_NOTHING, related_name='user_actions_on_content')

    @property
    def activity_actor_attr(self):
        return self.user

    @property
    def activity_verb(self):
        return self.verb

    @property
    def activity_object_attr(self):
        return self.object

    @property
    def created_at(self):
        return self.created


class UserFollowUser(TimeStampedModel):
    class Meta:
        db_table = 'user_follow_user'

    from_user = models.ForeignKey(to=User, null=True, on_delete=models.DO_NOTHING, related_name='following')
    to_user = models.ForeignKey(to=User, null=True, on_delete=models.DO_NOTHING, related_name='followed_by')


def follow_feed(sender, instance, created, **kwargs):
    if created:
        feed_manager.follow_user(instance.from_user_id, instance.to_user_id)


signals.post_save.connect(follow_feed, sender=UserFollowUser)


