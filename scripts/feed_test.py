from alexa.models import UserFollowUser, Joke, UserActOnContent, User
from stream_django.feed_manager import feed_manager
from stream_django.enrich import Enrich

enricher = Enrich()


def setup_follows():
    print("Following Part!")

    user_1 = User.objects.get(id=1)
    user_2 = User.objects.get(id=2)
    following1 = UserFollowUser.objects.filter(from_user=user_1, to_user=user_2)

    following2 = UserFollowUser.objects.filter(from_user=user_2, to_user=user_1)

    if not following1:
        print('no follow1 relation, creating it...')
        following1 = UserFollowUser(from_user=user_1, to_user=user_2)
        following1.save()

    if not following2:
        print('no follow2 relation, creating it...')
        following2 = UserFollowUser(from_user=user_2, to_user=user_1)
        following2.save()

    print("Act Creation...")

    joke = Joke.objects.get(id=2)

    act = UserActOnContent(user=user_1, verb='laughed', object=joke)
    act.save()


def see_user_feeds():
    print("See User Feeds")
    user_1 = User.objects.get(id=1)
    feeds = feed_manager.get_user_feed(user_1.id)

    activities = feeds.get()['results']
    print(activities)


def see_timeline():
    print("See Timeline")
    user_2 = User.objects.get(id=2)
    feeds = feed_manager.get_news_feeds(user_2.id)
    activities = feeds.get('timeline').get()['results']
    enriched_activities = enricher.enrich_activities(activities)
    print(enriched_activities)


def run():
    setup_follows()
    see_user_feeds()
    see_timeline()
