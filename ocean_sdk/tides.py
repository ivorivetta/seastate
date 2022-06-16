import logging
from noaa_tidesandcurrents import TidesAndCurrentsApi
from exceptions import OceanSDKException
from models import Result
from datetime import datetime

class TideApi:
    def __init__(self, ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for TideApi, composed with TidesAndCurrentsApi 

        Args:
            hostname (str, optional): Set to api.tidesandcurrents.noaa.gov.
            api_key (str, optional): Not used. Defaults to ''.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self.api = TidesAndCurrentsApi( ssl_verify, logger)
    
    @property
    def api(self):
        
        
    def coordinates():
        # todo, location of selected measurement
        pass
        
    def hourly(self, station:str, start:datetime, end: datetime) -> Result:
        return result

        
if __name__ == '__main__':
    tideapi = TideApi()
    result = tideapi.tides_hourly(9410230, datetime.today(),datetime.today())
    print(result)
    # import pdb
    # pdb.set_trace()