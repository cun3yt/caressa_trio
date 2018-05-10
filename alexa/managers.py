"""
The usage is like this: `Action.objects.mystream(user, circle)`. The return type is `GFKQuerySet`.
"""
from actstream.managers import stream, ActionManager
from alexa.models import Circle, User


class ActionManagerByCircle(ActionManager):

    @stream
    def mystream(self, user: User, circle: Circle):
        if not circle.is_member(user):
            return None

        return self.user(circle.person_of_interest, with_user_activity=True).exclude(actor_object_id=user.id)
