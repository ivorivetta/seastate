import logging
from datetime import datetime, timedelta
from typing import Dict, Union

# from pandas import DataFrame

# from seastate.exceptions import SeaStateException
from seastate.api.api_mediator import ApiMediator

logging.basicConfig(level=logging.DEBUG)

class SeaState:
    def __init__(self, lat: float, lon: float, exclude: list=[], logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self.exclude = list(exclude)
        self.tide = ApiMediator('tide', self.lat, self.lon, self.exclude)
        self.wind = ApiMediator('wind', self.lat, self.lon, self.exclude)
        self.water_temp = ApiMediator('water_temp', self.lat, self.lon, self.exclude)
        self.air_temp = ApiMediator('air_temp', self.lat, self.lon, self.exclude)
        self.air_press = ApiMediator('air_press', self.lat, self.lon, self.exclude)
        self.wave = ApiMediator('wave', self.lat, self.lon, self.exclude)
        self.conductivity = ApiMediator('conductivity', self.lat, self.lon, self.exclude)
        
    def measurements_from_date_range(self, start: datetime = None, end: Union[datetime, timedelta] = None) -> Dict:
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
            
        # remove microseconds to pass comparison tests
        # remove hours and minutes from start
        # set hours and minutes to end of day for start
        if isinstance(start,datetime):
            start = start.replace(microsecond=0)
            start = start.replace(hour=0, minute=0)
        if isinstance(end,datetime):
            end = end.replace(microsecond=0)
            end = end.replace(hour=23, minute=0)
            
        # log warning if end is before start
        if end > start:
            self._logger.warning("end is after start")
        
        # Get data
        data = {}
        #todo: have a class property that summarizes the active apis for this list
        for api_key in ['tide', 'wind', 'water_temp', 'air_temp', 'air_press', 'wave', 'conductivity']:
            # access the configured api to generate response with hourly method 
            data[api_key] = self.__getattribute__(api_key).api.measurements_from_date_range(
                measurement = self.__getattribute__(api_key).measurement,
                station_id = self.__getattribute__(api_key).station.id,
                start = start,
                end = end)
        return data

    def hourly(self, start: datetime = None, end: Union[datetime, timedelta] = None) -> Dict:
        """Convenience method to return 1 sample per hour for each api

        Args:
            start (datetime, optional): _description_. Defaults to None.
            end (Union[datetime, timedelta], optional): _description_. Defaults to None.

        Returns:
            Dict: _description_
        """
        data_all = self.measurements_from_date_range(start,end)
        data= {}
        for key in data_all:
            # find the first minute within the hour
            # the apis typically use the same minute 
            first_minute = 0
            while not datetime.fromisoformat(data_all[key][0]['t']).minute == first_minute:
                first_minute += 1
                # prevent endless loop 
                if first_minute == 60:
                    data[key] = []
                    continue
            # keep one reading per hour
            data[key] = [x for x in data_all[key] if datetime.fromisoformat(x['t']).minute == first_minute]
        return data
    
if __name__ == '__main__':
    api = SeaState(32,-117)
    # start = datetime(2022,7,5)
    # end = datetime(2022,7,5)
    # a = test.hourly(start,end)
    
    # check daterange within realtime
    result = api.hourly(datetime.today()-timedelta(days=2),datetime.today())
    
    # check daterange for request only in prior years
    # result = api.hourly(datetime.today()-timedelta(days=2*365+30),datetime.today()-timedelta(days=1*365+30))

    # check daterange spanning archive and realtime, into prior year
    # result = api.hourly(datetime.today()-timedelta(days=365+30),datetime.today())
    
    # check old archive with different headers
    # check date format
    # result = api.hourly('air_press',42040,datetime(1996,2,1),datetime(1996,2,2))

    pass
