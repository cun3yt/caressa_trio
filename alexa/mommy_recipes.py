from model_mommy.recipe import Recipe, foreign_key, seq
from alexa.models import User, Song, Circle, CircleMembership

user = Recipe(
    User,
    first_name='TestFirstName1',
    last_name='TestLastName1',
    email=seq('user1@example.com'),
    phone_number='+14151234567',
    profile_pic='TestProfilePic1',
    state='TestState1',
    city='TestCity1',
)

user2 = Recipe(
    User,
    first_name='TestFirstName2',
    last_name='TestLastName2',
    email=seq('user2@example.com'),
    phone_number='+11112223344',
    profile_pic='TestProfilePic2',
    state='TestState2',
    city='TestCity2',
)

song = Recipe(
    Song,
    artist='TestArtist1',
    duration=180,
    file_name='static/song/test.mp3',
    title='TestSong1',
    genre='Rock',
)

circle = Recipe(
    Circle,
    person_of_interest_id=foreign_key(user)
)

circle_membership = Recipe(
    CircleMembership,
    isAdmin=False,
    circle_id=foreign_key(circle),
    circle_membership=foreign_key(user)
)
