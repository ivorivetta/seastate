import logging
from typing import Dict, Union
from exceptions import OceanSDKException
from noaa_tides import TideApi
from datetime import datetime, timedelta
from utils import nearest_station
from pandas import DataFrame

logging.basicConfig(level=logging.DEBUG)

class OceanState:
    def __init__(self, lat: float, lon: float, logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self._tide_api = TideApi()
        self.tide_station_nearest = nearest_station('tide', self.lat, self.lon)
        
    def get_hourly(self, start: datetime = None, end: Union[datetime, timedelta] = None) -> Dict:
        # Process timeframe
        # todo: handle iso date strings
        # todo: handle bad date strings
        if start and end: # all values provided, handle endpoint
            if isinstance(end, datetime):
                pass
            elif isinstance(end, timedelta):
                end = start + end
        elif start and not end: # no end provided, return same day as start
            end = start
        elif not start and not end: # nothing provided, return today
            start = datetime.today()
            end = datetime.today()
        
        # Get data
        # todo: if status_code is good, return
        tide = self._tide_api.get_hourly(self.tide_station_nearest, start, end)
        return tide
    
    def get_hourly_df(self, start: datetime = None, end: datetime = None) -> Dict:
        data = self.get_hourly(start,end)
        
        # todo: unpack into dataframe
        df = DataFrame()
        
        return data

if __name__ == '__main__':
    test = OceanState(32,-117)
    result = test.get_hourly()
    print(result)
    import pdb
    pdb.set_trace()
        
