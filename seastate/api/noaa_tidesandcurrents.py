import logging
from datetime import datetime
from typing import Dict

from seastate.api.rest_adapter import RestAdapter
from seastate.exceptions import SeaStateException
from seastate.models import Result

logging.basicConfig(level=logging.DEBUG)

class TidesAndCurrentsApi:
    def __init__(self, api_key: str = '', ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for TidesAndCurrentsApi, composed with RestAdapter 

        Args:
            api_key (str, optional): Not used here. Defaults to ''.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter('api.tidesandcurrents.noaa.gov', api_key, ssl_verify, logger)
        
    def measurements_from_date_range(self, measurement:str, station_id:str, start:datetime, end: datetime) -> Result:
        """Returns Result for station ID and datetime start and end. Args should be validated externally

        Args:
            measurement (str): measurement type can be tide|wind|water_temp|air_temp|air_press|conductivity|tide_prediction.
            station_id (str): Station ID.
            start (datetime): start datetime.
            end (datetime): end datetime.

        Raises:
            SeaStateException: _description_

        Returns:
            Result: _description_
        """
        
        # each measurement type will have a different endpoint "product" param and key to unpack response
        # always test str on lowercase casting
        measurement = measurement.lower()
        if 'tide' in measurement:
            product = 'water_level'
            measurement_key = 'data'
        elif 'wind' in measurement:
            product = 'wind'
            measurement_key = 'data'
        elif 'water_temp' in measurement:
            product = 'water_temperature'
            measurement_key = 'data'
        elif 'air_temp' in measurement:
            product = 'air_temperature'
            measurement_key = 'data'
        elif 'air_press' in measurement:
            product = 'air_pressure'
            measurement_key = 'data'
        elif 'wave' in measurement:
            raise SeaStateException("Unsupported measurement requested")
        elif 'conductivity' in measurement:
            product = 'conductivity'
            measurement_key = 'data'
        else:
            raise SeaStateException("Unsupported measurement requested")

        # formatting datetime to endpoint param
        begin_date = f"{start.year}{start.month:02}{start.day:02}"
        end_date = f"{end.year}{end.month:02}{end.day:02}"
        
        ep_params = {
            'begin_date': begin_date,
            'end_date': end_date,
            'station': str(station_id),
            'product': product,
            'interval': 'h',
            'datum': 'MTL',
            'units': 'metric',
            'time_zone': 'lst_ldt',
            'application': 'seastate',
            'format': 'json',
        }
        
        # Call endpoint
        endpoint='api/prod/datagetter?'
        result = self._rest_adapter.get(endpoint=endpoint,ep_params=ep_params)
        
        # unpack to return specified measurement
        # since TidesAndCurrents returns 1 product per endpoint, no need to parse, just unpack Json
        # details here: https://api.tidesandcurrents.noaa.gov/api/prod/responseHelp.html
        # 
        try:
            data = result.data[measurement_key]
        except (KeyError) as e:
            self._logger.error(result.data)
            raise SeaStateException("TidesAndCurrentsApi unpacking error") from e
        
        return Result(status_code=result.status_code, message = result.message, data=data)
    
    def hourly(self, measurement:str, station_id:str, start:datetime, end: datetime) -> Dict:
        result = self.measurements_from_date_range(measurement, station_id, start, end)
        # todo: filter results hourly
        if result.status_code == 200:
            return result.data
        pass

        
if __name__ == '__main__':
    api = TidesAndCurrentsApi()
    result = api.hourly('wind',9410230, datetime.today(),datetime.today())
    print(result)
    # result = api.hourly(9410230, datetime.today(),datetime.today(),'air_temp')
    # print(result)
    # result = api.hourly(9410230, datetime.today(),datetime.today(),'water_temp')
    # print(result)
    # import pdb
    # pdb.set_trace()
