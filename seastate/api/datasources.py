import logging
from html.parser import HTMLParser
from typing import List

import defusedxml.minidom
from seastate.api.rest_adapter import RestAdapter
from seastate.api.noaa_ndbc import NdbcApi
from seastate.api.noaa_tidesandcurrents import TidesAndCurrentsApi
from seastate.exceptions import SeaStateException
from seastate.models import Station


class DataSources:
    def __init__(self, logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        
    def all(self) -> List[Station]:
        """Convenience function for all stations

        Returns:
            List[Station]: _description_
        """
        stations = self.ndbc_stations()
        stations += self.tides_and_currents_stations()
        return stations
    
    def ndbc_stations(self) -> List[Station]:
        """Parse a text table

        Returns:
            List[Station]: _description_
        """
        # check station status by retrieving latest measurements from all stations
        result = RestAdapter('www.ndbc.noaa.gov/').get('data/latest_obs/latest_obs.txt')
        
        # loop through text lines and test if station is ouputting specified measurement
        stations = []
        for i, value in enumerate(result.data.split('\n')):
            # skipping 2 header lines
            if i == 0:
                continue #skip header
            elif i == 1:
                continue #skip units
            
            # split current line by delimiter and clear empty values
            line = value.split(' ')    
            while ' ' in line:
                line.remove(' ')
            while '' in line:
                line.remove('')
            
            # skip corrupted lines
            if len(line) != 22:
                self._logger.info("No station info in this line: " + str(line))
                continue

            # parse stationID, gps, and confirm active measurement sources
            # 'MM' is NOAA's notation for missing measurement
            stations.append(Station(
                id= line[0],
                lat= float(line[1]),
                lon= float(line[2]),
                api= NdbcApi(),
                tide= True if line[21] != 'MM' else False,
                wind= True if line[8] != 'MM' else False,
                # wind_dir= True if line[9] != 'MM' else False,
                # wind_gust= True if line[10] != 'MM' else False,
                water_temp= True if line[18] != 'MM' else False,
                air_temp= True if line[17] != 'MM' else False,
                air_press= True if line[15] != 'MM' else False,
                wave= True if line[11] != 'MM' else False,
            ))
        
        # return list of stations
        return stations

    def tides_and_currents_stations(self) -> List[Station]:
        """Parse xml doc

        Raises:
            SeaStateException: _description_

        Returns:
            List[Station]: _description_
        """
        # TidesAndCurrent station capabilities are kept here
        result = RestAdapter('opendap.co-ops.nos.noaa.gov/').get('stations/stationsXML.jsp')
        
        # parse xml elements safely with defusedxml -> []
        dom = defusedxml.minidom.parseString(result.data)
        station_elements = dom.getElementsByTagName('station')
        
        # traverse station elements to build Station objects
        stations = []
        for line in station_elements:
            foo = {}
            # parse station metadata into temporary dict
            try:
                foo['name'] = line.getAttribute('name')
                foo['id'] = line.getAttribute('ID')
                foo['lat'] = float(line.getElementsByTagName('lat')[0].firstChild.nodeValue)
                foo['lon'] = float(line.getElementsByTagName('long')[0].firstChild.nodeValue)
                foo['api'] = TidesAndCurrentsApi()
            except (IndexError) as e:
                # Faulty station, skip station node
                # todo: refactor into object to properly log parsing errors
                continue
            
            # separate loop to parse individual measurements
            for m in line.getElementsByTagName('parameter'):
                name = m.attributes['name'].value
                status = True if m.attributes['status'].value == '1' else False
                if 'Water Level' in name and status:
                    foo['tide'] = True
                elif 'Winds' in name and status:
                    foo['wind'] = True
                    # todo: wind dir and gust may or may not be true
                elif 'Air Temp' in name and status:
                    foo['air_temp'] = True
                elif 'Water Temp' in name and status:
                    foo['water_temp'] = True
                elif 'Air Pressure' in name and status:
                    foo['air_press'] = True
                elif 'Conductivity' in name and status:
                    foo['conductivity'] = True
                else:
                    pass          

            # construct station with temp var
            stations.append(Station(**foo))
            
        # Check parsing was succesful
        if len(stations) == 0:
            raise SeaStateException("No stations successfully parsed, please submit issue")
        return stations

if __name__ == '__main__':
    tnc = DataSources().tides_and_currents_stations()
    ndbc = DataSources().ndbc_stations()
    pass
    # import pdb
    # pdb.set_trace()
    