import logging
from rest_adapter import RestAdapter
from exceptions import OceanSDKException
from models import *

class TideApi:
    baseurl = 'api.tidesandcurrents.noaa.gov/'
    ep = 'api/prod/datagetter?'
    
    def __init__(self, hostname: str = baseurl, api_key: str = '', ver: str = 'v1', ssl_verify: bool = True, logger: logging.Logger = None):
        self._rest_adapter = RestAdapter(hostname, api_key, ver, ssl_verify, logger)
        
    def get_hourly_json(self, ep: str = ep) -> JsonResult:
        ep_params = {
            'begin_date': '20220528',
            'end_date': '20220528',
            'station': '9410230',
            'product': 'predictions',
            'interval': 'h',
            'datum': 'MTL',
            'units': 'metric',
            'time_zone': 'lst_ldt',
            'application': 'ocean_sdk',
            'format': 'json',
        }
        result = self._rest_adapter.get(endpoint=ep,ep_params=ep_params)
        json = JsonResult(status_code=result.status_code, message = result.message, data=result.data)
        return json
        
    
if __name__ == '__main__':
    tideapi = TideApi()
    result = tideapi.get_hourly_json()
    print(result)
    print(result.data)
    print(type(result.data))
    import pdb
    pdb.set_trace()