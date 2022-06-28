from dataclasses import dataclass
from typing import List, Dict, Any

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
    api: Any
    tide: bool = False
    wind_spd: bool = False
    wind_dir: bool = False
    wind_gust: bool = False
    water_temp: bool = False
    air_temp: bool = False
    air_press: bool = False
    wave: bool = False
    conductivity: bool = False
    isActive: bool = False
    name: str = ''
    
    def __post_init__(self):
        # toggle if self.isActive
        if len(self.supported_measurements()) > 0:
            self.isActive = True
            
    def supported_measurements(self) -> List[str]:
        """Return list of supported measurements for station

        Returns:
            List[str]: _description_
        """
        # hash of Result.key:formal measurement name mapping
        hash_map = {
            'tide': 'Tide',
            'wind_spd': 'Wind Speed',
            'wind_dir': 'Wind Direction',
            'wind_gust': 'Wind Gust',
            'water_temp': 'Water Temp',
            'air_temp': 'Air Temp',
            'air_press': 'Air Press',
            'wave': 'Wave',
            'conductivity': 'Conductivity',
        }
        # return list of measurements where True
        supported = []
        for key in hash_map:
            if self.__getattribute__(key):
                supported.append(hash_map[key])
        return supported
        
        
        
        
    
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

    