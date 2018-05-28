from django.db import models
from actstream.models import Action
from model_utils.models import TimeStampedModel
from alexa.models import User


class UserAction(Action):
    """
    This proxy Action model adds extra representation abilities for API/serializer
    """
    class Meta:
        proxy = True

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

    comment = models.TextField(null=False, blank=False)
    owner = models.ForeignKey(to=User, on_delete=models.DO_NOTHING, related_name='comments')
    content = models.ForeignKey(to=UserAction, on_delete=models.DO_NOTHING, related_name='action_comments')

    def __repr__(self):
        return "Comment({}) by {}: {}".format(self.id, self.owner, self.comment)

    def __str__(self):
        return "{} commented on {}: {}".format(self.owner, self.content, self.comment)


Comment._meta.get_field('created').db_index = True


