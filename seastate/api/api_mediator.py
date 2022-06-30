import logging
from datetime import datetime
from typing import Any, Tuple

from seastate.api.datasources import DataSources
from seastate.exceptions import OceanSDKException
from seastate.models import Result, Station
from seastate.utils import haversine

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
        self._target_lat = lat
        self._target_lon = lon
        self.include = include
        self.exclude = exclude
        self.measurement = measurement
        self.station = self.nearest_station()
        self.api = self.station.api
        self.distance = haversine(self._target_lat,self._target_lon, self.station.lat, self.station.lon)

    def nearest_station(self) -> Station:
        # Return dict of stations
        # n<2000 so just return them all
        try:
            # Return all stations
            stations = DataSources().all()
        except (KeyError) as e:
            raise OceanSDKException("Error retrieving stations") from e

        # Find station closest to input coordinates using haversine
        # and is also active for specified measurement
        min = float('inf') # Initialize minimum pointer
        for eval_station in stations:
            # skip if eval_station is inactive
            if not eval_station.isActive:
                continue
            # skip if station does not support measurement
            if not eval_station.isSupported(self.measurement):
                continue
            # compute distance between SeaState coords and current station
            new_val = haversine(self._target_lat, self._target_lon, eval_station.lat, eval_station.lon)
            # if closer, update new minimum
            if new_val < min:
                min = new_val
                station = eval_station
        return station



if __name__ == '__main__':
    api = ApiMediator('Tide',32,-117) # testing San Diego for tide
    # Station should have tide as a valid measurement
    assert api.station.tide
    assert api.station.isSupported(api.measurement)
    # out of bound lat/lon should throw errors
    
    # testing wind
    api = ApiMediator('Wind',32,-117) # testing San Diego for tide
    
    pass
