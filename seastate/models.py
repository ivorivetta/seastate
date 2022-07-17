from dataclasses import dataclass, field
from typing import List, Dict, Any

# the implemented measurements for 
valid_measurements = {
    'tide',
    'wind',
    'water_temp',
    'air_temp',
    'air_press',
    'wave',
    'conductivity',
}

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
    data: List[Dict] = field(default_factory=list)
    
    def __post__init__(self, data):
        self.data = data if data else [] #init data if dne

@dataclass
class Station:
    id: str
    lat: float
    lon: float
    api: Any
    tide: bool = False
    wind: bool = False
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
        # 
        supported = []
        for key in valid_measurements:
            if self.__getattribute__(key):
                supported.append(key)
        return supported
        
    def isSupported(self, value:str) -> bool:
        # Implemented this to always run comparison on lower case casting of strings
        for x in self.supported_measurements():
            if value in x:
                return True
        return False
        
        
if __name__ == '__main__':
    # Result tests
    test = Result(200)
    
    # Station Tests
    test = Station()
    # test internal methods