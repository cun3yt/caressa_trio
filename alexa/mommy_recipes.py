from model_mommy.recipe import Recipe, foreign_key
from alexa.models import User, AUser, EngineSession

user = Recipe(
    User,
    first_name='TestFirstName1',
    last_name='TestLastName1',
    email='TestEMail1',
    phone_number='+14151234567',
    profile_pic='TestProfilePic1'
)

auser = Recipe(
    AUser,
    alexa_id='TestAlexaId1',
    user=foreign_key(user),
    engine_schedule='TestEngineSchedule',
)

engine_session = Recipe(
    EngineSession,
    user=foreign_key(auser),
    name='TestEngine1',
    state='continue',
    data={},
    ttl=600,
)
