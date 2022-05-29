from dataclasses import dataclass
from typing import List, Dict

@dataclass
class JsonResult:
    """Simplified requests.Response returned from RestAdapter

    Args:
        status_code (int): HTTP Status
        message (str, optional): Human redable result. Defaults to ''.
        data (List[Dict], optional): Pyrhon list of Dicts. Defaults to None.
    """
    status_code: int
    message: str = ''
    data: List[Dict] = None
    
    def __post__init__(self, data):
        self.data = data if data else [] #init data if dne


class Prediction:
    def __init__(self, t: str, v: str) -> None:
        self.t = t
        self.v = v


class Tides:
    def __init__(self, predictions: List[Prediction]) -> None:
        self.predictions = predictions
