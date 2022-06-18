import logging
from rest_adapter import RestAdapter
from exceptions import OceanSDKException
from models import Result
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

class TidesAndCurrentsApi:
    def __init__(self, api_key: str = '', ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for TidesAndCurrentsApi, composed with RestAdapter 

        Args:
            hostname (str, optional): Set to api.tidesandcurrents.noaa.gov.
            api_key (str, optional): Not used. Defaults to ''.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter('api.tidesandcurrents.noaa.gov/', api_key, ssl_verify, logger)
        
    def hourly(self, station:str, start:datetime, end: datetime, category:str) -> Result:
        """Returns Result for stationID and datetime start and end. Args should be validated externally

        Args:
            station (str): Station ID.
            start (datetime): start datetime.
            end (datetime): end datetime.
            category (str): measurement type can be tide|wind|water_temp|air_temp.

        Raises:
            OceanSDKException: _description_

        Returns:
            Result: _description_
        """
        # datetime formatting for endpoint param
        begin_date = f"{start.year}{start.month:02}{start.day:02}"
        end_date = f"{end.year}{end.month:02}{end.day:02}"
        
        # category string handling for endpoint and result unpacking
        if 'tide' in category:
            product = key = 'predictions'
        elif 'wind' in category:
            product = 'wind'
            key = 'data'
        elif 'air_temp' in category:
            product = 'air_temperature'
            key = 'data'
        elif 'water_temp' in category:
            product = 'water_temperature'
            key = 'data'
        else:
            raise OceanSDKException("Unsupported measurement requested")

        
        ep_params = {
            'begin_date': begin_date,
            'end_date': end_date,
            'station': str(station),
            'product': product,
            'interval': 'h',
            'datum': 'MTL',
            'units': 'metric',
            'time_zone': 'lst_ldt',
            'application': 'ocean_sdk',
            'format': 'json',
        }
        
        # Call endpoint
        result = self._rest_adapter.get(endpoint='api/prod/datagetter?',ep_params=ep_params)
        
        # unpack
        try:
            data = result.data[key]
        except (KeyError) as e:
            self._logger.error(result.data)
            raise OceanSDKException("TidesAndCurrentsApi unpacking error") from e
        result = Result(status_code=result.status_code, message = result.message, data=data)
        
        return result

        
if __name__ == '__main__':
    api = TidesAndCurrentsApi()
    result = api.hourly(9410230, datetime.today(),datetime.today(),'wind')
    print(result)
    # result = api.hourly(9410230, datetime.today(),datetime.today(),'air_temp')
    # print(result)
    # result = api.hourly(9410230, datetime.today(),datetime.today(),'water_temp')
    # print(result)
    # import pdb
    # pdb.set_trace()