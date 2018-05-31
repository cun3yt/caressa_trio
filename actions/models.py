from django.db import models
from actstream.models import Action
from model_utils.models import TimeStampedModel
from alexa.models import User
from django.utils.translation import ugettext as _


class UserAction(Action):
    """
    This proxy Action model adds extra representation abilities for API/serializer
    """
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(UserAction, self).__init__(*args, **kwargs)

    def __str__(self):
        ctx = {
            'actor': self.actor,
            'verb': self.verb,
            'action_object': self.action_object,
            'timesince': self.timesince()
        }
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s %(timesince)s ago') % ctx
        return _('%(actor)s %(verb)s %(timesince)s ago') % ctx

    @property
    def statement(self):
        return self.__str__()

    @property
    def action_object_type(self):
        return type(self.action_object).__name__ if self.action_object else None

    @property
    def number_of_comments(self):
        return self.action_comments.count()


class Comment(TimeStampedModel):
    class Meta:
        db_table = 'action_comment'

    comment = models.TextField(null=False,
                               blank=False, )
    owner = models.ForeignKey(to=User,
                              on_delete=models.DO_NOTHING,
                              related_name='comments', )
    content = models.ForeignKey(to=UserAction,
                                on_delete=models.DO_NOTHING,
                                related_name='action_comments', )

    def __repr__(self):
        return "Comment({}) by {}: {}".format(self.id, self.owner, self.comment)

    def __str__(self):
        return "{} commented on {}: {}".format(self.owner, self.content, self.comment)


Comment._meta.get_field('created').db_index = True


class UserReaction(TimeStampedModel):
    class Meta:
        db_table = 'user_reaction'

    reaction = models.CharField(max_length=100,
                                db_index=True,
                                default='like', )
    owner = models.ForeignKey(to=User,
                              on_delete=models.DO_NOTHING,
                              related_name='reactions',
                              db_index=True, )
    content = models.ForeignKey(to=UserAction,
                                on_delete=models.DO_NOTHING,
                                related_name='action_reactions',
                                db_index=True, )

    def __repr__(self):
        return "Reaction({}) by {}: {}".format(self.id, self.owner, self.reaction)

    def __str__(self):
        return "{} did reaction '{}' on {}".format(self.owner, self.reaction, self.content)
