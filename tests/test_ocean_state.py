from unittest import TestCase, mock
from ocean_sdk.ocean_state import OceanState
from ocean_sdk.models import Result
from ocean_sdk.exceptions import OceanSDKException
import requests

def TestOceanState(TestCase):
    def setUp(self):
        # La Jolla test case
        self._ocean_state = OceanState(32,-117)
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
        
    def test_bad_measure_raises_keyerror(self):
        assert False
        
    def test_bad_timestring_raises_typeerror(self):
        assert False
        
    def test_bad_timeoffset_raises_typeerror(self):
        assert False


