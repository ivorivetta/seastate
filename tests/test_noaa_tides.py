from doctest import testsource
from unittest import TestCase, mock
from ocean_sdk.noaa_tides import TideApi
from ocean_sdk.models import Result
from ocean_sdk.exceptions import OceanSDKException
import requests

def TestTideApi(TestCase):
    def setUp(self):
        self._tide_api = TideApi()
        self.response = requests.Response()
        
    # get_hourly
    
    def test_good_call_returns_result(self):
        assert False
        
    def test_bad_category_raises_keyerror(self):
        assert False
        
    def test_bad_timestring_raises_typeerror(self):
        assert False
        
    def test_bad_timezone_raises_typeerror(self):
        assert False


