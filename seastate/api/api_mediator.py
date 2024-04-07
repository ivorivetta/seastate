from typing import Union
from dataclasses import field
import logging

from seastate.data import STATIONS
from seastate.exceptions import SeaStateException
from seastate.models import Station
from seastate.utils import haversine
from seastate.api.base import BaseApi
from seastate.api.noaa_ndbc import NdbcApi
from seastate.api.noaa_tidesandcurrents import TidesAndCurrentsApi
from abc import ABC, abstractmethod


class BaseMediator(ABC):
    """Implements utils for finding nearest station and API for that station"""

    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def station(self) -> Station:
        pass

    @abstractmethod
    def api(self) -> BaseApi:
        pass

    @abstractmethod
    def distance(self) -> float:
        pass

    @property
    def _target_lat(self) -> None:
        return self.__target_lat

    @_target_lat.setter
    def _target_lat(self, value) -> None:
        #  Latitudes exist in range of -90 to 90
        if -90 <= value <= 90:
            self.__target_lat = value
        else:
            raise SeaStateException("Latitude must be between -90 and 90 degrees")

    @property
    def _target_lon(self) -> None:
        return self.__target_lon

    @_target_lon.setter
    def _target_lon(self, value) -> None:
        #  Longitudes exist in range of -180 to 180
        if -180 <= value <= 180:
            self.__target_lon = value
        else:
            raise SeaStateException("Longitude must be between -180 and 180 degrees")

    def _nearest_station(self) -> Station:
        """
        Find station that:
        - is closest to input coordinates using haversine method
        - is collecting the measurement at present (active)
        """
        station = None
        min_ptr = float("inf")  # Initialize minimum pointer at inf
        for eval_station in STATIONS:
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
            new_val = haversine(
                self._target_lat, self._target_lon, eval_station.lat, eval_station.lon
            )
            # if closer, update new minimum
            if new_val < min_ptr:
                min_ptr = new_val
                station = eval_station
        return station


class ApiMediator(BaseMediator):
    """_summary_"""

    def __init__(
        self,
        measurement: str,
        lat: float,
        lon: float,
        exclude: list = field(default_factory=list),
        logger: logging.Logger = None,
    ):
        self._target_lat = lat
        self._target_lon = lon
        self.measurement = measurement
        self.exclude = exclude
        # self._register_mediator(self)
        self._logger = logger or logging.getLogger(__name__)

    @property
    def station(self) -> Station:
        return self._nearest_station()

    @property
    def api(self) -> Union[NdbcApi, TidesAndCurrentsApi]:
        if self.station.api == "noaa_ndbc":
            return NdbcApi()
        elif self.station.api == "noaa_tidesandcurrents":
            return TidesAndCurrentsApi()
        else:
            raise SeaStateException("Unsupported API")

    @property
    def distance(self) -> float:
        return haversine(
            self._target_lat, self._target_lon, self.station.lat, self.station.lon
        )


if __name__ == "__main__":
    api = ApiMediator("Tide", 32, -117)  # testing San Diego for tide
    # Station should have tide as a valid measurement
    assert api.station.tide
    assert api.station.is_supported(api.measurement)
    # out of bound lat/lon should throw errors

    # testing wind
    api = ApiMediator("Wind", 32, -117)  # testing San Diego for tide
