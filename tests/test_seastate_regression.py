from seastate import SeaState
from datetime import datetime, timedelta
import pytest
from seastate.settings import MEASUREMENTS

# todo: add reg test for historical endpoints
# todo: cover ndbc and tnc datasources
# todo: write unit test for when result = emtpy, return [] and logger warning, for both datasources


class TestSeaState:
    @pytest.fixture
    def seastate(self):
        return SeaState(35.81468, -122.78828)

    # timestamps
    start = datetime(2023, 10, 5)
    end = datetime(2023, 10, 6)
    delta = timedelta(days=1)
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    @pytest.mark.parametrize(
        "start, end",
        [
            (today, today),
            (yesterday, yesterday),
            # (start, end),
        ],
    )
    def test_from_date_range_success(self, seastate, start, end):
        # should return a dict with keys matching MEASUREMENTS
        data = seastate.from_date_range(start, end)
        assert set(data.keys()) == set(MEASUREMENTS)


# Prev test cases
# https://www.ndbc.noaa.gov/data/realtime2/42040.txt
# https://www.ndbc.noaa.gov/data/stdmet/May/42040.txt
# https://www.ndbc.noaa.gov/view_text_file.php?filename=42040h1996.txt.gz&dir=data/historical/stdmet/
# https://www.ndbc.noaa.gov/view_text_file.php?filename=42040h1999.txt.gz&dir=data/historical/stdmet/
# https://www.ndbc.noaa.gov/data/realtime2/1801589.txt
