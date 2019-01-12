from django.db import models
from django.db.models import Q
from django.db.models import signals
from actstream import action
from actstream.models import Action
from model_utils.models import TimeStampedModel
from alexa.models import User, Joke, News, Circle, Song
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField
from utilities.logger import log
import timeago
from django.utils import timezone
from caressa.hardcodings import HC_CIRCLE_ID


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

    def __repr__(self):
        return "Comment({}) by {}: {}".format(self.id, self.comment_backers, self.comment)

    def __str__(self):
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


class ManualUserPost(TimeStampedModel):
    class Meta:
        db_table = 'manual_user_post'

    user = models.ForeignKey(to=User,
                             on_delete=models.DO_NOTHING,
                             related_name='manual_posts',
                             db_index=True,
                             help_text='Who (the circle member) is the content about?', )
    content_to_be_spoken = models.TextField(null=False,
                                            blank=False,
                                            help_text='The content to be spoken on Alexa. Put {timeago} '
                                                      'for time past since `Content Creation Time`', )
    content_creation_time = models.DateTimeField(null=False,
                                                 blank=False,
                                                 help_text='The date/time that the user content was created '
                                                           '(e.g. Facebook post time)', )
    yes_no_question = models.TextField(null=False,
                                       blank=False,
                                       help_text='Yes/No question that is presented after the content is spoken on '
                                                 'Alexa.', )
    yes_reflection_on_circle = models.TextField(null=False,
                                                blank=False,
                                                help_text='The presentation of the Alexa user\'s yes response '
                                                          'to the circle if "Yes" is said. ', )
    is_published = models.BooleanField(default=False,
                                       help_text='The post will not be presented on Alexa until it is published', )
    listened_time = models.DateTimeField(null=True,
                                         default=None,
                                         db_index=True,
                                         help_text='When the central person (e.g. senior) listened the content. '
                                                   'Once the content is listened, it will not be spoken again. '
                                                   'If you\'d like to re-publish a spoken content, '
                                                   'create a new manual post instead of re-publishing it', )

    def delete_related_activities(self):
        user_post_ct = ContentType.objects.get_for_model(ManualUserPost)
        actions = UserAction.objects.filter(Q(action_object_content_type=user_post_ct)
                                            & Q(action_object_object_id=self.id)).all()
        actions.delete()

    def __repr__(self):
        return 'ManualUserPost({}) by {}'.format(self.id, self.user)

    def __str__(self):
        time_ago_str = timeago.format(self.content_creation_time, timezone.now())
        return self.content_to_be_spoken.format(timeago=time_ago_str)


def manual_user_activity_save(sender, instance, created, **kwargs):
    post = instance     # type: ManualUserPost
    user = post.user    # type: User

    # todo if listened better disable for edit!!
    if post.listened_time:
        log('ManualUserPost::{id} is already listened, so NO new activity stream'.format(id=instance.id))
        return

    if not created:
        post.delete_related_activities()

    if not post.is_published:
        log('ManualUserPost::{id} is saved but not published yet, so NO activity stream'.format(id=instance.id))
        return

    circle = user.circle_set.all()[0]
    action.send(user,
                verb='created a post',
                description=kwargs.get('description', ''),
                action_object=post,
                target=circle, )


def manual_user_pre_delete(sender, instance, using, **kwargs):
    post = instance     # type: ManualUserPost
    post.delete_related_activities()


signals.post_save.connect(receiver=manual_user_activity_save,
                          sender=ManualUserPost, )


# There is a database model truncation in actstream but we have manual deletion in case.
signals.pre_delete.connect(receiver=manual_user_pre_delete,
                           sender=ManualUserPost, )


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
        username = self.user.first_name
        lst = ["{} {}".format(obj.get('verb', ''), obj.get('target', '')) for obj in self.data]
        if len(lst) <= 1:
            return "{} is {}".format(username, lst[0])
        return "I am {} and {}".format(', '.join(lst[:-1]), lst[-1])


def user_post_activity_save(sender, instance, created, **kwargs):
    circle_id = HC_CIRCLE_ID
    action.send(instance.user,
                verb='created a post',
                description=kwargs.get('description', ''),
                action_object=instance,
                target=Circle.objects.get(id=circle_id),
                )


signals.post_save.connect(receiver=user_post_activity_save, sender=UserPost)


class UserListened(TimeStampedModel):
    class Meta:
        db_table = 'user_listened'

    action = models.ForeignKey(UserAction, on_delete=models.DO_NOTHING)
