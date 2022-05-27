from typing import List, Dict

class Result:
    def __init__(self, status_code: int, message: str = '', data: List[Dict] = None):
        """Facade for requests.Response 

        Args:
            status_code (int): HTTP Status
            message (str, optional): Defaults to ''.
            data (List[Dict], optional): Defaults to None.
        """
        self.status_code = int(status_code)
        self.message = str(message)
        self.data = data if data else []