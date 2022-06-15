import logging
from rest_adapter import RestAdapter
from exceptions import OceanSDKException
from models import Result
from datetime import datetime

class TideApi:
    def __init__(self, api_key: str = '', ver: str = 'v1', ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for TideApi, composed with RestAdapter 

        Args:
            hostname (str, optional): Set to api.tidesandcurrents.noaa.gov.
            api_key (str, optional): Not used. Defaults to ''.
            ver (str, optional): Defaults to 'v1'.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter('api.tidesandcurrents.noaa.gov/', api_key, ver, ssl_verify, logger)
        
    def tides_hourly(self, station:str, start:datetime, end: datetime) -> Result:
        """Returns Result for stationID and datetime start and end

        Args:
            station (str): Station ID.
            start (datetime): start datetime.
            end (datetime): end datetime.

        Raises:
            OceanSDKException: _description_

        Returns:
            Result: _description_
        """
        
        # endpoint param formatting
        begin_date = f"{start.year}{start.month:02}{start.day:02}"
        end_date = f"{end.year}{end.month:02}{end.day:02}"
        
        ep_params = {
            'begin_date': begin_date,
            'end_date': end_date,
            'station': str(station),
            'product': 'predictions',
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
            data = result.data['predictions']   # key for tide predictions
        except (KeyError) as e:
            self._logger.error(result.data)
            raise OceanSDKException("TideApi unpacking error") from e
        
        result = Result(status_code=result.status_code, message = result.message, data=data)
        return result

        
if __name__ == '__main__':
    tideapi = TideApi()
    result = tideapi.tides_hourly(9410230, datetime.today(),datetime.today())
    print(result)
    # import pdb
    # pdb.set_trace()