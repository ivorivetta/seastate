import logging
from datetime import datetime
from typing import Any, Tuple

from exceptions import OceanSDKException
from models import Result
from seastate.api.noaa_tidesandcurrents import TidesAndCurrentsApi
from utils import haversine
from seastate.api.datasources import DataSources

logging.basicConfig(level=logging.DEBUG)


    # mediator behavior
        ## todo filters
        # if include and exclude is blank, default is closest and active for __name__
        # if 'inactive' in include, poll inactive stations as well?
        # if include is not empty, only include modules specified
        # if include is not empty, only include data sources specified
        # if exclude is not empty, exclude data sources and modules specified
        # if a specific stationID is specified, exclude that


class ApiMediator:
    def __init__(self, measurement: str, lat: float, lon: float, include: list=[], exclude: list=[], ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for configured api endpoint based on measurement type, gps coordinates and include/exclude filters 
        """
        self._ssl_verify = ssl_verify
        self._logger = logger or logging.getLogger(__name__)
        self.measurement = measurement
        self.station = '' # overridden by api setter, can be set manually
        self.api = (lat, lon, include, exclude) # pass to property setter
        
    @property
    def api(self):
        return self._api
    
    @api.setter
    def api(self, value):
        """_summary_

        Args:
            value (_type_): _description_
        """
        # unpack tuple
        lat, lon, include, exclude = value
        # select closest station and associated api
        self.station, self.api = self.nearest_station('tide', lat, lon, include, exclude)
        # self._api = TidesAndCurrentsApi()


    def nearest_station(measurement: str, lat: float, lon: float, include: list=[], exclude: list=[]) -> Tuple[str, Any]:
        """Returns nearest station from list

        Args:
            measurement (str): Measurement type for switching data source
                [tide]
            lat (float): Coordinate in decimal degrees
            lon (float): Coordinate in decimal degrees

        Raises:
            KeyError: _description_
            
        Returns:
            str: Unique station ID
        """
        # Select measurement and return dict of stations
        try:
            # Return all stations
            stations = DataSources.all()
        except (KeyError) as e:
            raise OceanSDKException("No Category found") from e

        # Find station closest to input coordinates using haversine
        # and is also active for specified measurement
        min = float('inf') # Initialize minimum pointer
        for station in stations:
            # skip if station is inactive
            if not station.isActive:
                continue
            # skip if station does not support measurement
            if measurement not in station.supported_measurements():
                continue
            # compute distance between SeaState coords and current station
            new_val = haversine(lat, lon, station.lat, station.lon)
            # if closer, update new minimum
            if new_val < min:
                min = new_val
                id = station.id
                api = station.api
        return id, api



if __name__ == '__main__':
    api = ApiMediator(32,-117)
    result = api.hourly(datetime.today(),datetime.today())
    # print(result)
    import pdb
    pdb.set_trace()
