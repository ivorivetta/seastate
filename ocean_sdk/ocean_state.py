import logging
from exceptions import OceanSDKException
from noaa_tides import TideApi
from datetime import datetime
from utils import nearest_station

logging.basicConfig(level=logging.DEBUG)

class OceanState:
    def __init__(self, lat: float, lon: float, logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self.tz = '+0' #todo: derive timezone from lat or if provided, align timezones
        self._tide_api = TideApi()
        self.tide_station_nearest = nearest_station('tide', self.lat, self.lon)
        
    def get_hourly(self, start: datetime = None, end: datetime = None):
        # Process timeframe
        if start and end: # all values provided, all good
            pass
        elif start and not end: # no end provided, return same day as start
            end = start
        elif not start and not end: # nothing provided, return today
            start = datetime.today()
            end = datetime.today()
        
        # Get data
        tide = self._tide_api.get_hourly(self.tide_station_nearest, start, end)
        return tide

if __name__ == '__main__':
    test = OceanState(32,-117)
    result = test.get_hourly()
    print(result)
    import pdb
    pdb.set_trace()
        
