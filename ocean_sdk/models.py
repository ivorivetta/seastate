from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Result:
    """Simplified requests.Response returned from RestAdapter

    Args:
        status_code (int): HTTP Status
        message (str, optional): Human readable result. Defaults to ''.
        data (List[Dict], optional): Python list of Dicts. Defaults to None.
    """
    status_code: int
    message: str = ''
    data: List[Dict] = None
    
    def __post__init__(self, data):
        self.data = data if data else [] #init data if dne

@dataclass
class Station:
    id: str
    lat: float
    lon: float
    tide: bool
    wind_spd: bool
    wind_dir: bool
    wind_gust: bool
    water_temp: bool
    air_temp: bool
    air_press: bool
    wave: bool
    isActive: bool = False
    name: str = ''
    
    def __post__init__(self, tide, wind_spd, water_temp, air_temp, air_press, wave):
        if tide or wind_spd or water_temp or air_temp or air_press or wave:
            self.isActive = True # Mark active if any viable measurement sources exist
    
# @dataclass
# class Wave:
#     wind_height: float
#     wind_period: float
#     swell_height: float
#     swell_period: float
#     # harmonic: list
    
# @dataclass
# class Wind:
#     wind_dir: float
#     wind_spd: float
#     wind_gust: float

    