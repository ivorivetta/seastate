import logging
from datetime import datetime

from api.api_mediator import ApiMediator
from exceptions import OceanSDKException
from models import Result

logging.basicConfig(level=logging.DEBUG)

class WindApi(ApiMediator):
    def __init__(self, lat: float, lon: float, include: list=[], exclude: list=[], ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for WindApi, inherits the following from ApiMediator:
            .api - configured rest adapter
            .measurement - measurement type
            .station - measurement station ID

        Args:
            lat (float): _description_
            lon (float): _description_
            include (list, optional): _description_. Defaults to [].
            exclude (list, optional): _description_. Defaults to [].
            ssl_verify (bool, optional): _description_. Defaults to True.
            logger (logging.Logger, optional): _description_. Defaults to None.
        """
        super().__init__('wind', lat, lon, include, exclude, ssl_verify, logger)
        
    def hourly(self, start:datetime, end: datetime) -> Result:
        result = self.api.hourly(self.measurement, self.station, start, end)
        return result

        
if __name__ == '__main__':
    api = WindApi(32,-117)
    result = api.hourly(datetime.today(),datetime.today())
    # print(result)
    import pdb
    pdb.set_trace()
