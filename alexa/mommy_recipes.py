from model_mommy.recipe import Recipe, foreign_key, seq
from alexa.models import User, Song, Circle, CircleMembership
from senior_living_facility.mommy_recipes import senior_living_facility_recipe

user = Recipe(
    User,
    first_name='TestFirstName1',
    last_name='TestLastName1',
    email=seq('user1@example.com'),
    phone_number='+14151234567',
    profile_pic='',
    state='TestState1',
    city='TestCity1',
    senior_living_facility=foreign_key(senior_living_facility_recipe),  # todo: make sure this is used for either senior or facility member
)

user2 = Recipe(
    User,
    first_name='TestFirstName2',
    last_name='TestLastName2',
    email=seq('user2@example.com'),
    phone_number='+11112223344',
    profile_pic='',
    state='TestState2',
    city='TestCity2',
)

family_user = Recipe(
    User,
    user_type=User.FAMILY,
    first_name='Family',
    last_name='User',
    email=seq('family_user@example.com'),
    phone_number='+4155554433',
    profile_pic='',
    state='Arkansas',
    city='Little Rock',
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
    person_of_interest=foreign_key(user)
)

circle_membership = Recipe(
    CircleMembership,
    isAdmin=False,
    circle_id=foreign_key(circle),
    circle_membership=foreign_key(user)
)
