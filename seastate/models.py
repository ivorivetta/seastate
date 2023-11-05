from dataclasses import dataclass, field
from typing import List, Dict
from seastate.settings import MEASUREMENTS


@dataclass
class Result:
    """Simplified requests.Response returned from RestAdapter

    Args:
        status_code (int): HTTP Status
        message (str, optional): Human readable result. Defaults to ''.
        data (List[Dict], optional): Python list of Dicts. Defaults to None.
    """

    status_code: int
    message: str = None
    data: List[Dict] = field(default_factory=list)

    def __post__init__(self, data):
        self.data = data if data else []  # init data if dne


@dataclass
class Station:
    id: str
    lat: float
    lon: float
    api: str
    name: str = None
    tide: bool = False
    wind: bool = False
    water_temp: bool = False
    air_temp: bool = False
    air_press: bool = False
    wave: bool = False
    conductivity: bool = False
    is_active: bool = False

    def __post_init__(self):
        # toggle if self.is_active
        if len(self.supported_measurements()) > 0:
            self.is_active = True

    def supported_measurements(self) -> tuple[str]:
        """Return list of supported measurements for station"""
        #
        supported = []
        for key in MEASUREMENTS:
            if self.__getattribute__(key):
                supported.append(key)
        return tuple(supported)

    def is_supported(self, value: str) -> bool:
        # Implemented this to always run comparison on lower case casting of strings
        for x in self.supported_measurements():
            if value in x:
                return True
        return False
