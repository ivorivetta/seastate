from seastate import SeaState
from datetime import datetime, timedelta
import pytest
from seastate.settings import MEASUREMENTS


class TestSeaState:
    @pytest.fixture
    def seastate(self):
        return SeaState(32, -117)

    @pytest.fixture
    def seastate_exclude(self):
        return SeaState(32, -117, exclude=["tide", "13009", "noaa_ndbc"])

    # Tests
    def test_set_mediators_success(self, seastate_exclude):
        # all measurements should be set as attributes
        # -> intersection of measurements and __dict__ should be length of measurements
        keys = set([x for x in seastate_exclude.__dict__.keys()])
        intersection = [x for x in keys if x in MEASUREMENTS]
        assert len(MEASUREMENTS) == len(intersection)

    def test_exclude_measurement_success(self, seastate_exclude):
        # assert seastate does not have tide
        assert seastate_exclude.tide is None

    @pytest.mark.skip
    def test_exclude_station_success(self, seastate_exclude):
        assert False

    @pytest.mark.skip
    def test_exclude_api_success(self, seastate_exclude):
        assert False

    start = datetime(2023, 10, 5)
    end = datetime(2023, 10, 6)
    delta = timedelta(days=1)

    @pytest.mark.parametrize(
        "start, end, expected",
        [
            (start, end, 2 * 24 * 60 * 60 - 1),
            (start, delta, 2 * 24 * 60 * 60 - 1),
            (start, None, 1 * 24 * 60 * 60 - 1),
            (None, None, 1 * 24 * 60 * 60 - 1),
        ],
    )
    def test_build_date_range_success(self, seastate, start, end, expected):
        # simplistic test,
        # should return a daterange with width 2 days or 1 day, minus 1 second
        start, end = seastate._build_date_range(start, end)
        assert (end - start).total_seconds() == expected
