from model_mommy.recipe import Recipe, foreign_key
from alexa.models import User, AUser, EngineSession, Song, Circle, CircleMembership

user = Recipe(
    User,
    first_name='TestFirstName1',
    last_name='TestLastName1',
    email='TestEMail1',
    phone_number='+14151234567',
    profile_pic='TestProfilePic1',
    state='TestState1',
    city='TestCity1',
)

user2 = Recipe(
    User,
    first_name='TestFirstName2',
    last_name='TestLastName2',
    email='TestEMail2',
    phone_number='+11112223344',
    profile_pic='TestProfilePic2',
    state='TestState2',
    city='TestCity2',
)

auser = Recipe(
    AUser,
    alexa_user_id='TestAlexaUserId1',
    alexa_device_id='TestAlexaDeviceId1',
    user=foreign_key(user),
    engine_schedule='TestEngineSchedule',
)

auser2 = Recipe(
    AUser,
    alexa_user_id='TestAlexaUserId2',
    alexa_device_id='TestAlexaDeviceId2',
    user=foreign_key(user2),
    engine_schedule='TestEngineSchedule',
)

engine_session = Recipe(
    EngineSession,
    user=foreign_key(auser2),
    name='TestEngine1',
    state='continue',
    data={},
    ttl=600,
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

