import logging
from rest_adapter import RestAdapter
from exceptions import OceanSDKException
from models import Result
from datetime import datetime

class TideApi:
    baseurl = 'api.tidesandcurrents.noaa.gov/'
    endpoint = 'api/prod/datagetter?'
    
    def __init__(self, hostname: str = baseurl, api_key: str = '', ver: str = 'v1', ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for TideApi, composed with RestAdapter 

        Args:
            hostname (str, optional): Set to api.tidesandcurrents.noaa.gov.
            api_key (str, optional): Not used. Defaults to ''.
            ver (str, optional): Defaults to 'v1'.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter(hostname, api_key, ver, ssl_verify, logger)
        
    def get_hourly(self, station:str, start:datetime, end: datetime, endpoint: str = endpoint) -> Result:
        """Returns Result for stationID and datetime start and end

        Args:
            station (str): Station ID.
            start (datetime): start datetime.
            end (datetime): end datetime.
            endpoint (str, optional): Defaults to endpoint.

        Raises:
            OceanSDKException: _description_

        Returns:
            Result: _description_
        """
            
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
        result = self._rest_adapter.get(endpoint=endpoint,ep_params=ep_params)
        
        # unpack
        try:
            data = result.data['predictions']
        except (KeyError) as e:
            self._logger.error(result.data)
            raise OceanSDKException("TideApi unpacking error") from e
        result = Result(status_code=result.status_code, message = result.message, data=data)
        return result

        
if __name__ == '__main__':
    tideapi = TideApi()
    result = tideapi.get_hourly()
    print(result)
    import pdb
    pdb.set_trace()