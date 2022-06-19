from unittest import TestCase, mock
from ocean_sdk.noaa_tides import TideApi
from ocean_sdk.models import Result
from ocean_sdk.exceptions import OceanSDKException
import requests

def TestTideApi(TestCase):
    def setUp(self):
        self._tide_api = TideApi()
        self.response = requests.Response()
        
    # hourly tests
    def test_good_call_returns_result(self):
        assert False
        
    def test_good_df_call_returns_df(self):
        assert False
        
    def test_empty_call_raises_error(self):
        assert False
    
    # measure switch
    def test_bad_measure_raises_keyerror(self):
        assert False
    
    # time window feature
    def test_no_timestring_raises_valueerror(self):
        assert False
            
    def test_bad_timestring_raises_typeerror(self):
        assert False
        
    def test_historic_timeframe_is_handled(self):
        assert False
    
    # time offset feature
    def test_good_call_with_timeoffset_returns_result(self):
        assert False
        
    def test_bad_timeoffset_raises_typeerror(self):
        assert False


