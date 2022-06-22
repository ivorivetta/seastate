import logging
from datetime import datetime, timedelta
from typing import Dict, Union

from pandas import DataFrame

from exceptions import OceanSDKException
from tide import TideApi
from wind import WindApi

logging.basicConfig(level=logging.DEBUG)

class OceanState:
    def __init__(self, lat: float, lon: float, include: list=[], exclude: list=[], logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self.include = include
        self.exclude = exclude
        self.tide = TideApi(self.lat, self.lon, self.include, self.exclude)
        self.wind = WindApi(self.lat, self.lon, self.include, self.exclude)
        
    def hourly(self, start: datetime = None, end: Union[datetime, timedelta] = None) -> Dict:
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
        tide = self.tide.hourly(start, end)
        return tide
    
    # def hourly_df(self, start: datetime = None, end: datetime = None) -> Dict:
    #     data = self.hourly(start,end)
        
    #     # todo: unpack into dataframe
    #     df = DataFrame()
        
        return data

if __name__ == '__main__':
    test = OceanState(32,-117)
    result = test.hourly()
    print(result)
    import pdb
    pdb.set_trace()
