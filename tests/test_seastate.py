from unittest import TestCase, mock
from seastate.seastate import SeaState
from seastate.models import Result
from seastate.exceptions import SeaStateException
import requests

def TestSeaState(TestCase):
    def setUp(self):
        # La Jolla test case
        self._ocean_state = SeaState(32,-117)
        self.response = requests.Response()
        
# Prev test cases
# https://www.ndbc.noaa.gov/data/realtime2/42040.txt
# https://www.ndbc.noaa.gov/data/stdmet/May/42040.txt
# https://www.ndbc.noaa.gov/view_text_file.php?filename=42040h1996.txt.gz&dir=data/historical/stdmet/
# https://www.ndbc.noaa.gov/view_text_file.php?filename=42040h1999.txt.gz&dir=data/historical/stdmet/

