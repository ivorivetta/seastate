import logging
from datetime import datetime, timedelta
from typing import Dict, Union

from pandas import DataFrame

from seastate.exceptions import SeaStateException
from seastate.api.api_mediator import ApiMediator

logging.basicConfig(level=logging.DEBUG)

class SeaState:
    def __init__(self, lat: float, lon: float, include: list=[], exclude: list=[], logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self.include = list(include)
        self.exclude = list(exclude)
        self.tide = ApiMediator('tide', self.lat, self.lon, self.include, self.exclude)
        self.wind = ApiMediator('wind', self.lat, self.lon, self.include, self.exclude)
        self.water_temp = ApiMediator('water_temp', self.lat, self.lon, self.include, self.exclude)
        self.air_temp = ApiMediator('air_temp', self.lat, self.lon, self.include, self.exclude)
        self.air_press = ApiMediator('air_press', self.lat, self.lon, self.include, self.exclude)
        self.wave = ApiMediator('wave', self.lat, self.lon, self.include, self.exclude)
        self.conductivity = ApiMediator('conductivity', self.lat, self.lon, self.include, self.exclude)
        
    def hourly(self, start: datetime = None, end: Union[datetime, timedelta] = None) -> Dict:
        # Process timeframe
        # todo: handle iso date strings
        # todo: handle bad date strings
        if start and end: # all values provided, handle endpoint
            # end can be declared relative to start as a timedelta
            if isinstance(end, datetime):
                pass
            elif isinstance(end, timedelta):
                end = start + end
        elif start and not end: # no end provided, return same day as start
            end = start
        elif not start and not end: # nothing provided, return today
            start = datetime.today()
            end = datetime.today()
            
        # raise exception if end is before start
        if end > start:
            raise SeaStateException("end date is after start")
        
        # raise exception if end is in the future
        if end > datetime.today():
            raise SeaStateException("End date is in the future, SeaState object does not perform forecasting")
        
        # Get data
        data = {}
        #todo: have a class property that summarizes the active apis for this list
        for api_key in ['tide', 'wind', 'water_temp', 'air_temp', 'air_press', 'wave', 'conductivity']:
            # access the configured api to generate response with hourly method 
            data[api_key] = self.__getattribute__(api_key).api.hourly(
                measurement = self.__getattribute__(api_key).measurement,
                station_id = self.__getattribute__(api_key).station.id,
                start = start,
                end = end)
        return data

if __name__ == '__main__':
    test = SeaState(32,-117)
    start = datetime(2022,7,5)
    end = datetime(2022,7,5)
    a = test.hourly(start,end)
    pass
