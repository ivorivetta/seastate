from curses.ascii import GS
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
    wind: bool
    water_temp: bool
    air_temp: bool
    name: str = ''
    

    