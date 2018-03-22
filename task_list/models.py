from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.db import models
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from task_list.queue import get_alexa_user_communication_queue
from django_fsm import FSMField, transition
from model_utils import Choices


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

    phone_number = PhoneNumberField(db_index=True)

    def is_senior(self):
        return self.user_type == self.CARETAKER

    def is_family(self):
        return self.user_type == self.FAMILY

    def is_provider(self):
        return self.user_type in (self.CAREGIVER, self.CAREGIVER_ORG)


class SomeState(models.Model):
    class Meta:
        db_table = 'some_state'

    STATUS = Choices('draft', 'approved', 'published', 'removed')

    state = FSMField(
        default=STATUS.draft,
        verbose_name='Publication State',
        choices=STATUS,
        protected=True,
    )

    can_display = models.BooleanField(default=False)

    def is_displayable(self):
        return self.can_display

    @transition(field=state, source=[STATUS.approved],
                target=STATUS.published,
                conditions=[is_displayable])
    def publish(self):
        print('published')

    @transition(field=state, source=[STATUS.draft],
                target=STATUS.approved)
    def approve(self):
        print('approved')


class AlexaUser(TimeStampedModel):
    class Meta:
        db_table = 'alexa_user'

    alexa_id = models.TextField(db_index=True, editable=False)
    user = models.ForeignKey(to=User, null=True, on_delete=models.DO_NOTHING, related_name='alexa_users')
    state = JSONField(default={"unfinished_tasks": {}, "engines": {}})

    def get_communication_queue(self):
        return get_alexa_user_communication_queue(self.id)

    def get_last_request(self):
        last_session = self.sessions.order_by('-created').last()

        if not last_session:
            return None

        req = last_session.alexa_requests.order_by('-created').last()
        return req if req else None

    def get_last_engine_request(self, engine_type):
        pass


class AlexaSession(TimeStampedModel):
    class Meta:
        db_table = 'alexa_session'

    alexa_id = models.TextField(db_index=True, editable=False)
    alexa_user = models.ForeignKey(to='AlexaUser', on_delete=models.CASCADE, related_name='sessions')
    number = models.IntegerField(default=0)     # todo delete this
    state = JSONField(default={})


AlexaSession._meta.get_field('created').db_index = True


class AlexaRequest(TimeStampedModel):
    class Meta:
        db_table = 'alexa_request'

    session = models.ForeignKey(AlexaSession, related_name='alexa_requests', on_delete=models.SET_NULL, null=True)
    request = JSONField(null=False)
    engine = models.TextField(null=True, blank=False, default=None)
    state = JSONField(default={})
    done_time = models.DateTimeField(null=True, default=None)


AlexaRequest._meta.get_field('created').db_index = True


class AlexaEngineLog(TimeStampedModel):
    class Meta:
        db_table = 'alexa_engine_log'

    alexa_user = models.ForeignKey(to=AlexaUser, on_delete=models.DO_NOTHING, related_name='alexa_engine_logs')
    engine = models.TextField(blank=False, null=False, db_index=True)
    is_done = models.BooleanField(default=False)
    payload = JSONField(default={})


AlexaEngineLog._meta.get_field('created').db_index = True
