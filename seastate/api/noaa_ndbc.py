import logging
from datetime import datetime, timedelta

from seastate.api.rest_adapter import RestAdapter
from seastate.exceptions import SeaStateException
from seastate.models import Result
from typing import Dict


class NdbcApi:
    def __init__(self, api_key: str = '', ssl_verify: bool = True, logger: logging.Logger = None):
        """Constructor for NdbcApi, composed with RestAdapter 

        Args:
            api_key (str, optional): Not used here. Defaults to ''.
            ssl_verify (bool, optional): Defaults to True.
            logger (logging.Logger, optional): Pass explictly else will be created with __name__.
        """
        self._logger = logger or logging.getLogger(__name__)
        self._rest_adapter = RestAdapter('www.ndbc.noaa.gov', api_key, ssl_verify, logger)
        
    def measurements_from_date_range(self, measurement:str, station_id:str, start:datetime, end: datetime) -> Result:
        """Returns Result for stationID and datetime start and end

        Args:
            station (str): station ID.
            start (datetime): start datetime.
            end (datetime): end datetime.

        Raises:
            SeaStateException: _description_

        Returns:
            Result: _description_
        """
        
        # todo: choose key for each measurement
        measurement = measurement.lower()
        if 'tide' in measurement:
            measurement_key = 'TIDE'
        elif 'wind' in measurement:
            #todo: handle 2d+ measurements
            measurement_key = 'WSPD'
        elif 'water_temp' in measurement:
            measurement_key = 'WTMP'
        elif 'air_temp' in measurement:
            measurement_key = 'ATMP'
        elif 'air_press' in measurement:
            measurement_key = 'PRES'
        elif 'conductivity' in measurement:
            raise SeaStateException("Unsupported measurement requested, please report issue")
        elif 'tide_prediction' in measurement:
            raise SeaStateException("Unsupported measurement requested, please report issue")
        else:
            raise SeaStateException("Unsupported measurement requested, please report issue")
        
        # Call endpoint
        cutoff_date = datetime.today() - timedelta(days=45)
        if start > cutoff_date or end > cutoff_date:
            # "realtime" endpoint covers prev 45 days
            endpoint = f"data/realtime2/{station_id}.txt"
            result = self._rest_adapter.get(endpoint=endpoint)
        else:
            # todo: handle endpoint for archival data
            raise SeaStateException("ndbc time range exceeded")
        
        # unpack result
        # ndbc reports are a text file with previous 45 days of measurements
        # todo: unpack text file into t: and v:
        try:
            data = []
            for i, value in enumerate(result.data.split('\n')):
                # turn str to list
                # known anomaly: 2 space characters sometimes delimiting 
                line = value.replace('  ', ' ').split(' ')
                while ' ' in line:
                    line.remove(' ') #remove blanks
                while '' in line:
                    line.remove('') #remove blanks
                
                # handle header lines
                if i == 0:
                    # column name in first line
                    header = line
                    # known anomaly, header starts with '#', remove from '#YY'
                    header[0] = header[0].strip('#')
                    continue
                elif i == 1:
                    # skipping units header line
                    continue
                
                # handle corrupted lines
                if len(line) != 19:
                    self._logger.info(f"ignoring line #{i}:{str(line)}")
                    continue
                
                # skip lines outside of daterange
                if not start.year <= int(line[0]) <= end.year:
                    continue
                if not start.month <= int(line[1]) <= end.month:
                    continue
                if not start.day <= int(line[2]) <= end.day:
                    continue
                
                # line has been requested
                # parse timestamp
                timestamp = datetime(
                    year=int(line[0]),
                    month=int(line[1]),
                    day=int(line[2]),
                    hour=int(line[3]),
                    minute=int(line[4])).isoformat()
                
                data.append({
                    't': timestamp,
                    'v': line[header.index(measurement_key)]
                              })
        except (KeyError) as e:
            self._logger.error(result.data)
            raise SeaStateException("NdbcApi unpacking error") from e

        return Result(status_code=result.status_code, message = result.message, data=data)

    def hourly(self, measurement:str, station_id:str, start:datetime, end: datetime) -> Dict:
        result = self.measurements_from_date_range(measurement, station_id, start, end)
        # todo: filter results hourly
        if result.status_code == 200:
            return result.data
        pass
        
if __name__ == '__main__':
    api = NdbcApi()
    result = api.hourly('wind',46224,datetime.today(),datetime.today())
    print(result)
    pass
    # import pdb
    # pdb.set_trace()
