import logging
from typing import Dict, Union
from exceptions import OceanSDKException
from tides import TideApi
from winds import WindApi
from datetime import datetime, timedelta
from utils import nearest_station
from pandas import DataFrame

logging.basicConfig(level=logging.DEBUG)

class OceanState:
    def __init__(self, lat: float, lon: float, include: list=[], exclude: list=[], logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self.include = include
        self.exclude = exclude
        self.tide = TideApi(self.lat, self.lon, include, exclude)
        self.wind = WindApi(self.lat, self.lon, include, exclude)
        
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

        # todo: move this to a mediator class and inherit?
        # todo: does util cover it?
        # mediator behavior
            ## filters
            # if include and exclude is blank, default is closest and active for __name__
            # if 'inactive' in include, poll inactive stations as well?
            # if include is not empty, only include modules specified
            # if include is not empty, only include data sources specified
            # if exclude is not empty, exclude data sources and modules specified
            # if a specific stationID is specified, exclude that
