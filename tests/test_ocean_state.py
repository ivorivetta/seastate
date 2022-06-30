from unittest import TestCase, mock
from seastate.seastate import SeaState
from seastate.models import Result
from seastate.exceptions import SeaStateException
import requests

def TestSeaState(TestCase):
    def setUp(self):
        # La Jolla test case
        self._ocean_state = SeaState(32,-117)
        self.response = requests.Response()
        
    # Tide Station Nearest
    def test_la_jolla_nearest_tide_station(self):
        assert False
        
    # hourly tests
    def test_good_call_returns_result(self):
        assert False
        
    def test_good_call_with_timeoffset_returns_result(self):
        assert False
        
    def test_good_df_call_returns_df(self):
        assert False
        
    def test_bad_measurement_raises_keyerror(self):
        assert False
        
    def test_bad_timestring_raises_typeerror(self):
        assert False
        
    def test_bad_timeoffset_raises_typeerror(self):
        assert False


