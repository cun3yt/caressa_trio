from model_mommy.recipe import Recipe, foreign_key, seq
from senior_living_facility.models import SeniorLivingFacility

senior_living_facility_recipe = Recipe(
    SeniorLivingFacility,
    name='Example Facility',
    facility_id=seq('so.cool.facility'),
)
