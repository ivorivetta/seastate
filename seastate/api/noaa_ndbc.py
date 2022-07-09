import logging
from datetime import datetime, timedelta

from seastate.api.rest_adapter import RestAdapter
from seastate.exceptions import SeaStateException
from seastate.models import Result
from typing import Dict, List


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
        
    def _parse_text(self, text:str, start:datetime, end: datetime) -> List[Dict]:
        pass
        
        
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
        elif 'wave' in measurement:
            #todo handle swell information
            measurement_key = 'WVHT'
        elif 'conductivity' in measurement:
            raise SeaStateException("Unsupported measurement requested, please report issue")
        else:
            raise SeaStateException("Unsupported measurement requested, please report issue")
        
        # Collect endpoints needed to cover daterange
        endpoints = []
        # daterange spans realtime endpoint (45 days)
        archive_cutoff_date = datetime.today() - timedelta(days=45)
        if start > archive_cutoff_date or end > archive_cutoff_date:
            # "realtime" endpoint covers prev 45 days
            endpoints += [f"data/realtime2/{station_id}.txt"]
        # daterange spans archive
        # within current year, endpoints are grouped by month
        if start < archive_cutoff_date and archive_cutoff_date.year == datetime.today().year:
            # use January if start year precedes the archive cutoff year
            # else use start month
            start_range = 1 if start.year < archive_cutoff_date.year else start.month
            # Endpoint uses abbreviated month designations
            requested_months = [datetime(month=x).strftime("%b") for x in range(start_range,archive_cutoff_date.month)]
            endpoints += [f"data/stdmet/{x}/{station_id}.txt" for x in requested_months]
        # prior years are collated into years
        if start < archive_cutoff_date and start.year < datetime.today().year:
            requested_years = [str(x) for x in range(start.year,end.year)]
            endpoints += [f"view_text_file.php?filename={station_id}h{x}.txt.gz&dir=data/historical/stdmet/" for x in requested_years]

        result = ''
        for endpoint in endpoints:
            res = self._rest_adapter.get(endpoint=endpoint)
            if res.status_code == 200:
                result += res.data
            else:
                self._logger.error(f"failed to retrieve endpoint {endpoint}")
                
                
        
        # unpack text result
        # realtime ndbc reports are a text file with previous 45 days of measurements
        # archival are a years worth
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
                if line[0] in ['#YY', 'YY']:
                    # column name starts with #YY in realtime, YY in archive
                    header = line
                    # strip '#' from '#YY'
                    header[0] = header[0].strip('#')
                    continue
                elif line[0] in ['#yr']:
                    # skipping units line
                    continue
                
                # handle corrupted lines
                if len(line) == 0:
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
                
                #todo: check for double entries between realtime and archive
                
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
    # check daterange = today
    result = api.hourly('wind',46224,datetime.today(),datetime.today())
    # check
    pass
    # import pdb
    # pdb.set_trace()
