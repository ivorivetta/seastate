import json
import logging
from dataclasses import asdict
from typing import List

import defusedxml.minidom

from seastate.api.noaa_ndbc import NdbcApi
from seastate.api.noaa_tidesandcurrents import TidesAndCurrentsApi
from seastate.api.rest_adapter import RestAdapter
from seastate.exceptions import SeaStateException
from seastate.models import Station


class StationParser:
    def __init__(self, logger: logging.Logger = None):
        self._logger = logger or logging.getLogger(__name__)

    @staticmethod
    def from_jsons(jsons: str) -> List[Station]:
        """Parses a json string into a list of Station objects"""
        return [Station(**x) for x in json.loads(jsons)]

    @staticmethod
    def to_jsons(stations: List[Station]) -> str:
        """Parses a list of Station object into a json str"""
        return json.dumps([asdict(x) for x in stations])

    def noaa_ndbc(self) -> List[Station]:
        """
        Calls the ndbc endpoint
        summarizes all observations and parses the station metadata
        """
        # todo: refactor this spaghetti code
        # check station status by retrieving latest measurements from all stations
        result = RestAdapter("www.ndbc.noaa.gov/").get("data/latest_obs/latest_obs.txt")

        # loop through text lines and test if station is ouputting specified measurement
        stations = []
        for i, value in enumerate(result.data.split("\n")):
            # skipping 2 header lines
            if i == 0 or i == 1:
                continue  # skip header and unit lines

            # split current line by delimiter and clear empty values
            line = value.split(" ")
            while " " in line:
                line.remove(" ")
            while "" in line:
                line.remove("")

            # skip corrupted lines
            if len(line) != 22:
                self._logger.info("No station info in this line: " + str(line))
                continue

            # parse stationID, gps, and confirm active measurement sources
            # 'MM' is NOAA's notation for missing measurement
            tmp_station = {
                "id": line[0],
                "lat": float(line[1]),
                "lon": float(line[2]),
                "api": NdbcApi().id,
                "tide": True if line[21] != "MM" else False,
                "wind": True if line[8] != "MM" else False,
                "water_temp": True if line[18] != "MM" else False,
                "air_temp": True if line[17] != "MM" else False,
                "air_press": True if line[15] != "MM" else False,
                "wave": True if line[11] != "MM" else False,
            }

            # construct station with temp var
            stations.append(Station(**tmp_station))

        # return list of stations
        return stations

    def noaa_tidesandcurrents(self) -> List[Station]:
        """
        Calls the tnc endpoint
        summarizes all stations and parses their metadata
        """
        # todo: refactor this spaghetti code
        # TidesAndCurrent station capabilities are kept here
        result = RestAdapter("opendap.co-ops.nos.noaa.gov/").get(
            "stations/stationsXML.jsp"
        )

        # parse xml elements safely with defusedxml -> []
        dom = defusedxml.minidom.parseString(result.data)
        station_elements = dom.getElementsByTagName("station")

        # traverse station elements to build Station objects
        stations = []
        for line in station_elements:
            tmp_station = {}
            # parse station metadata into temporary dict
            try:
                tmp_station["name"] = line.getAttribute("name")
                tmp_station["id"] = line.getAttribute("ID")
                tmp_station["lat"] = float(
                    line.getElementsByTagName("lat")[0].firstChild.nodeValue
                )
                tmp_station["lon"] = float(
                    line.getElementsByTagName("long")[0].firstChild.nodeValue
                )
                tmp_station["api"] = TidesAndCurrentsApi().id
            except IndexError as e:
                # Faulty station, skip station node
                self._logger.warn(e + str(line))
                continue

            # separate loop to parse individual measurements
            for m in line.getElementsByTagName("parameter"):
                name = m.attributes["name"].value
                status = True if m.attributes["status"].value == "1" else False
                if "Water Level" in name and status:
                    tmp_station["tide"] = True
                elif "Winds" in name and status:
                    tmp_station["wind"] = True
                    # todo: wind dir and gust may or may not be true
                elif "Air Temp" in name and status:
                    tmp_station["air_temp"] = True
                elif "Water Temp" in name and status:
                    tmp_station["water_temp"] = True
                elif "Air Pressure" in name and status:
                    tmp_station["air_press"] = True
                elif "Conductivity" in name and status:
                    tmp_station["conductivity"] = True

            # construct station with temp var
            stations.append(Station(**tmp_station))

        # Check parsing was succesful
        if len(stations) == 0:
            raise SeaStateException(
                "No stations successfully parsed, please submit issue"
            )
        return stations
