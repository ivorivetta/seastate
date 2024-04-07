from seastate.data.parsers import StationParser
import json
from tests.factories import StationFactory


class TestStationParser:
    TEST_LIST = [
        {"id": "Station A", "lat": 51.5074, "lon": -0.1278, "api": "noaa_ndbc"},
        {"id": "Station B", "lat": 52.5074, "lon": -1.1278, "api": "noaa_ndbc"},
    ]

    TEST_STRING = '[{"id": "Station A", \
        "lat": 51.5074, "lon": -0.1278, "api": "noaa_ndbc"},\
        {"id": "Station B", \
            "lat": 52.5074, "lon": -1.1278, "api": "noaa_ndbc"}]'

    def test_to_jsons_shallow_success(self):
        parser = StationParser()
        stations = [StationFactory().create(**x) for x in self.TEST_LIST]
        jsons = parser.to_jsons(stations)
        # just checking that length is the same, not full identity
        assert len(json.loads(jsons)) == len(self.TEST_LIST)

    def test_from_jsons_shallow_success(self):
        parser = StationParser()
        jsons = self.TEST_STRING
        stations = parser.from_jsons(jsons)
        # just checking that length is the same, not full identity
        assert len(stations) == 2
