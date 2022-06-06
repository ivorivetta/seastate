from unittest import TestCase, mock
from ocean_sdk.rest_adapter import RestAdapter
from ocean_sdk.models import Result
from ocean_sdk.exceptions import OceanSDKException
import requests

class TestRestAdapter(TestCase):
    def setUp(self):
        self.rest_adapter = RestAdapter()
        self.response = requests.Response()
    
    # _do
    def test__do_good_request_returns_result(self):
        self.response.status_code = 200
        self.response._content = "{}".encode()
        with mock.patch("requests.request", return_value=self.response):
            result = self.rest_adapter._do('GET', '')
            self.assertIsInstance(result, Result)
    
    def test__do_bad_json_raises_oceansdkexception(self):
        bad_json = '{"bad json": '
        self.response._content = bad_json
        with mock.patch("requests.request", return_value=self.response):
            with self.assertRaises(OceanSDKException):
                self.rest_adapter._do('GET', '')
        
        
        
        