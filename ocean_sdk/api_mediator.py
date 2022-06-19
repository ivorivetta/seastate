import logging
from datetime import datetime

from exceptions import OceanSDKException
from models import Result
from noaa_tidesandcurrents import TidesAndCurrentsApi
from utils import nearest_station

logging.basicConfig(level=logging.DEBUG)

class ApiMediator:
    def __init__(self, measure: str, lat: float, lon: float, include: list=[], exclude: list=[], ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for configured api endpoint based on measurement type, gps coordinates and include/exclude filters 
        """
        self._ssl_verify = ssl_verify
        self._logger = logger or logging.getLogger(__name__)
        self.measure = measure
        self.station = '' # overridden by api setter, can be overridden manually
        self.api = (lat, lon, include, exclude) # pass to property setter
        
    @property
    def api(self):
        return self._api
    
    @api.setter
    def api(self, value):
        # unpack tuple
        lat, lon, include, exclude = value
        # select api and station with closest station
        self._api = TidesAndCurrentsApi()
        self.station = nearest_station('tide', lat, lon, include, exclude)

        
if __name__ == '__main__':
    api = ApiMediator(32,-117)
    result = api.hourly(datetime.today(),datetime.today())
    # print(result)
    import pdb
    pdb.set_trace()
