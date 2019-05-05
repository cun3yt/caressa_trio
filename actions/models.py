from django.db import models
from django.db.models import signals
from actstream import action
from actstream.models import Action
from model_utils.models import TimeStampedModel
from alexa.models import User, Joke, Circle
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField


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

    comment_backers = models.ManyToManyField(to=User)

    content = models.ForeignKey(to=UserAction,
                                on_delete=models.DO_NOTHING,
                                related_name='action_comments', )

    def __repr__(self):     # todo does this work? Doesn't `comment_backers` create a problem?
        return "Comment({}) by {}: {}".format(self.id, self.comment_backers, self.comment)

    def __str__(self):     # todo does this work? Doesn't `comment_backers` create a problem?
        return "{} commented on {}: {}".format(self.comment_backers, self.content, self.comment)


Comment._meta.get_field('created').db_index = True


class CommentResponse(TimeStampedModel):
    class Meta:
        db_table = 'action_comment_conversation'

    response = models.TextField(null=False,
                                blank=False, )

    comment = models.ForeignKey(to=Comment,
                                on_delete=models.DO_NOTHING, )

    owner = models.ForeignKey(to=User,
                              on_delete=models.DO_NOTHING, )


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


class UserPost(TimeStampedModel):
    class Meta:
        db_table = 'user_post'

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING,
                             related_name='posts',
                             db_index=True, )
    data = JSONField(default=[])
    '''
    data is a JSON array of actions, e.g.
    [{"verb": "watch", "target": "Star Wars"},
     {"verb": "drink", "target": "Latte"},
     {"verb": "listen", "target": "Jazz"}]
    '''

    def __str__(self):
        name = self.user.first_name
        lst = ["{} {}".format(obj.get('verb', ''), obj.get('target', '')) for obj in self.data]
        if len(lst) <= 1:
            return "{} is {}".format(name, lst[0])
        return "I am {} and {}".format(', '.join(lst[:-1]), lst[-1])


def user_post_activity_save(sender: UserPost, instance, created, **kwargs):
    user = sender.user
    circle = user.circle_set[0] if user.circle_set.count() > 0 else None

    if circle:
        action.send(instance.user,
                    verb='created a post',
                    description=kwargs.get('description', ''),
                    action_object=instance,
                    target=circle,
                    )


signals.post_save.connect(receiver=user_post_activity_save, sender=UserPost)


class UserQuery(TimeStampedModel):
    class Meta:
        db_table = 'user_query'

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    message = JSONField(default={})
    resolution = models.TextField(null=False, blank=False, default='',
                                  help_text="How this case is resolved or what actions are taken so far. "
                                            "It is for Caressa Team usage only")
    solved = models.DateTimeField(null=True)
