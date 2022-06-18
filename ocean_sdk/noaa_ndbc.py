import logging
from rest_adapter import RestAdapter
from exceptions import OceanSDKException
from models import Result
from datetime import datetime, timedelta

class NdbcApi:
    def __init__(self, api_key: str = '', ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for NdbcApi, composed with RestAdapter 

        Args:
            hostname (str, optional): Set to https://www.ndbc.noaa.gov/.
            api_key (str, optional): Not used. Defaults to ''.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter('https://www.ndbc.noaa.gov/', api_key, ssl_verify, logger)
        
    def measurements_hourly(self, buoy:str, start:datetime, end: datetime) -> Result:
        """Returns Result for buoyID and datetime start and end

        Args:
            buoy (str): buoy ID.
            start (datetime): start datetime.
            end (datetime): end datetime.

        Raises:
            OceanSDKException: _description_

        Returns:
            Result: _description_
        """
        
        # Call endpoint
        if start|end < (datetime.today() - timedelta(days=45)):
            # "realtime" endpoint covers prev 45 days
            endpoint = f"/data/realtime2/{buoy}.txt"
            result = self._rest_adapter.get(endpoint=endpoint,ep_params=ep_params)
        else:
            # todo: handle endpoint for archival data
            raise OceanSDKException("ndbc time range exceeded")
            
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
        
        
        # unpack
        try:
            data = result.data['predictions']   # key for tide predictions
        except (KeyError) as e:
            self._logger.error(result.data)
            raise OceanSDKException("NdbcApi unpacking error") from e
        
        result = Result(status_code=result.status_code, message = result.message, data=data)
        return result

        
if __name__ == '__main__':
    api = NdbcApi()
    result = api.hourly(46224,datetime.today(),datetime.today())
    print(result)
    # import pdb
    # pdb.set_trace()