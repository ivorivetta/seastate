from seastate.models import Station
from dataclasses import dataclass
from faker import Faker
from seastate.settings import DATASOURCES


@dataclass
class StationFactory:
    class Meta:
        model = Station

    id = Faker("id")
    lat = Faker().latitude()
    lon = Faker().longitude()
    api = Faker().random_element(elements=DATASOURCES)

    def create(self, **kwargs):
        return self.Meta.model(**kwargs)
