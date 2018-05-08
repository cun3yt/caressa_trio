from alexa.models import UserActOnContent, Joke, User
from actstream import action
from actstream.actions import follow
from actstream.managers import FollowManager
from actstream.models import followers, user_stream, any_stream


user = User.objects.get(id=1)
user2 = User.objects.get(id=2)


def run_smt():
    joke = Joke.objects.get(id=5)
    act = UserActOnContent(user=user, verb='did', object=joke)
    act.save()


def run():
    # lst = followers(user)
    lst = any_stream(user)
    print(lst[2].target.punchline)


def run3():
    follow(user2, user)


def run2():
    joke = Joke.objects.get(id=5)
    action.send(user,
                verb='zibidi',
                data={'sss': 'zoko'},
                description='something happining',
                target=joke,
                action_object=joke,
                )
