from typing import List, Dict

class JsonResult:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        """Simplified requests.Response returned from RestAdapter

        Args:
            status_code (int): HTTP Status
            message (str, optional): Human redable result. Defaults to ''.
            data (List[Dict], optional): Pyrhon list of Dicts. Defaults to None.
        """
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []


class Prediction:
    def __init__(self, t: str, v: str) -> None:
        self.t = t
        self.v = v


class Tides:
    def __init__(self, predictions: List[Prediction]) -> None:
        self.predictions = predictions
