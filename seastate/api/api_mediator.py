from dataclasses import field
import logging

from seastate.api.datasources import DataSources
from seastate.exceptions import SeaStateException
from seastate.models import Station
from seastate.utils import haversine

class ApiMediator:
    def __init__(self, measurement: str, lat: float, lon: float, exclude: list = field(default_factory=list), ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for configured api endpoint based on measurement type, gps coordinates and exclude filters 
        """
        self._ssl_verify = ssl_verify
        self._logger = logger or logging.getLogger(__name__)
        self._target_lat = lat
        self._target_lon = lon
        self.exclude = exclude
        self.measurement = measurement
        self.station = self.nearest_station() # nearest_station handles the selection logic
        self.api = self.station.api
        self.distance = haversine(self._target_lat,self._target_lon, self.station.lat, self.station.lon)
        
    ## Properties
    @property
    def _target_lat(self):
        return self.__target_lat
    
    @_target_lat.setter
    def _target_lat(self,value):
        #  Latitudes are in range of -90 to 90
        if -90 <= value <= 90:
            self.__target_lat = value
        else:
            raise SeaStateException("Latitude must be between -90 and 90 degrees")
    
    @property
    def _target_lon(self):
        return self.__target_lon
    
    @_target_lon.setter
    def _target_lon(self,value):
        #  Longitudes are in range of -180 to 180
        if -180 <= value <= 180:
            self.__target_lon = value
        else:
            raise SeaStateException("Longitude must be between -180 and 180 degrees")

    # # Methods
    def nearest_station(self) -> Station:
        # if measurement
        # Return dict of stations
        # n<2000 so just return them all
        try:
            # Grab all stations
            stations = DataSources().all()
        except (KeyError) as e:
            raise SeaStateException("Error retrieving stations") from e

        # Find station closest to input coordinates using haversine
        # and is active for specified measurement
        min_ptr = float('inf') # Initialize minimum pointer
        for eval_station in stations:
            # skip if station is in exclude list
            if eval_station.id in self.exclude:
                continue
            # skip if eval_station is inactive
            if not eval_station.is_active:
                continue
            # skip if station does not support measurement
            if not eval_station.is_supported(self.measurement):
                continue
            # compute distance between SeaState target coords and current station
            new_val = haversine(self._target_lat, self._target_lon, eval_station.lat, eval_station.lon)
            # if closer, update new minimum
            if new_val < min_ptr:
                min_ptr = new_val
                station = eval_station
        return station



if __name__ == '__main__':
    api = ApiMediator('Tide',32,-117) # testing San Diego for tide
    # Station should have tide as a valid measurement
    assert api.station.tide
    assert api.station.is_supported(api.measurement)
    # out of bound lat/lon should throw errors
    
    # testing wind
    api = ApiMediator('Wind',32,-117) # testing San Diego for tide

