from html.parser import HTMLParser
import logging
from typing import List
import defusedxml.minidom
from ocean_sdk.models import Station
from ocean_sdk.exceptions import OceanSDKException
import requests

class DataSources:
    def __init__(self, logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)
        
    def ndbc_stations(self) -> List[Station]:
        """Parse a text table

        Returns:
            List[Station]: _description_
        """
        # request from realtimeOBS endpoint
        result = requests.get('https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt')
        
        # main loop
        stations = []
        for i, value in enumerate(result.iter_lines()):
            # parse data
            if i == 0:
                print(value)
                continue #skip header
            elif i == 1:
                continue #skip units
            line = value.decode().split(' ')
                
            # clean out empties
            while ' ' in line:
                line.remove(' ')
            while '' in line:
                line.remove('')
            
            # todo: check length
            if len(line) != 22:
                print('length off')
                print(line)
            
            # parse stationID, gps, and confirm active measurement sources
            # 'MM' is NOAA's notation for missing measurement
            stations.append(Station(
                id= line[0],
                lat= float(line[1]),
                lon= float(line[2]),
                tide= True if line[21] != 'MM' else False,
                wind_spd= True if line[8] != 'MM' else False,
                wind_dir= True if line[9] != 'MM' else False,
                wind_gust= True if line[10] != 'MM' else False,
                water_temp= True if line[18] != 'MM' else False,
                air_temp= True if line[17] != 'MM' else False,
                air_press= True if line[15] != 'MM' else False,
                wave= True if line[11] or line[12] or line[13] or line[14] != 'MM' else False,
            ))
        
        # return list of stations
        return stations

    def tides_and_currents_stations() -> List[Station]:
        """Parse xml doc

        Raises:
            OceanSDKException: _description_

        Returns:
            List[Station]: _description_
        """
        # request data from realtimeOBS endpoint
        result = requests.get('https://opendap.co-ops.nos.noaa.gov/stations/stationsXML.jsp')
        # parse safely with defusedxml
        dom = defusedxml.minidom.parseString(result.content.decode())
        station_elements = dom.getElementsByTagName('station')
        
        # traverse station elements
        stations = []
        for line in station_elements:
            temp = {}
            # parse station metadata into temporary dict
            try:
                temp['name'] = line.getAttribute('name')
                temp['id'] = line.getAttribute('ID')
                temp['lat'] = float(line.getElementsByTagName('lat')[0].firstChild.nodeValue)
                temp['lon'] = float(line.getElementsByTagName('long')[0].firstChild.nodeValue)
            except (IndexError) as e:
                # Faulty station, skip station node
                # todo: refactor into object to properly log parsing errors
                continue
            
            # separate loop to parse individual measurements
            for m in line.getElementsByTagName('parameter'):
                name = m.attributes['name'].value
                status = True if m.attributes['status'].value == '1' else False
                if 'Water Level' in name and status:
                    temp['tide'] = True
                elif 'Winds' in name and status:
                    temp['wind_spd'] = True
                    # todo: wind dir and gust may or may not be true
                elif 'Air Temp' in name and status:
                    temp['air_temp'] = True
                elif 'Water Temp' in name and status:
                    temp['water_temp'] = True
                elif 'Air Pressure' in name and status:
                    temp['air_press'] = True
                else:
                    pass          

            # construct station with temp var
            stations.append(Station(**temp))
        # Check parsing was succesful
        if len(stations) == 0:
            raise OceanSDKException("No stations successfully parsed, plz submit issue")
        return stations
    

if __name__ == '__main__':
    result = DataSources().tides_and_currents_stations()
    pass
    # import pdb
    # pdb.set_trace()
    