import logging
from datetime import datetime
from typing import Dict, Union

from seastate.api.base import BaseApi
from seastate.api.rest_adapter import RestAdapter
from seastate.exceptions import SeaStateException
from seastate.models import Result


class TidesAndCurrentsApi(BaseApi):
    def __init__(self, logger: logging.Logger = None):
        """Constructor for TidesAndCurrentsApi, composed with RestAdapter"""
        self._logger = logger or logging.getLogger(__name__)
        self._adapter = RestAdapter("api.tidesandcurrents.noaa.gov")

    def _build_parse_key(self, measurement: str = None) -> Union[str, list[str], None]:
        return "data"

    def _build_endpoint(
        self, measurement: str, station_id: str, start: datetime, end: datetime
    ) -> (str, Dict):
        # each measurement type will have a different endpoint "product" param
        # always test str on lowercase casting
        measurement = measurement.lower()
        if "tide" in measurement:
            product = "water_level"
        elif "wind" in measurement:
            product = "wind"
        elif "water_temp" in measurement:
            product = "water_temperature"
        elif "air_temp" in measurement:
            product = "air_temperature"
        elif "air_press" in measurement:
            product = "air_pressure"
        elif "wave" in measurement:
            raise SeaStateException("Unsupported measurement requested")
        elif "conductivity" in measurement:
            product = "conductivity"
        else:
            raise SeaStateException("Unsupported measurement requested")

        # formatting datetime to endpoint param
        begin_date = f"{start.year}{start.month:02}{start.day:02}"
        end_date = f"{end.year}{end.month:02}{end.day:02}"

        ep_params = {
            "begin_date": begin_date,
            "end_date": end_date,
            "station": str(station_id),
            "product": product,
            "interval": "h",
            "datum": "MTL",
            "units": "metric",
            "time_zone": "lst_ldt",  # todo: local time or gmt? what is ndbc doing?
            "application": "seastate",
            "format": "json",
        }

        # Call endpoint
        endpoint = "api/prod/datagetter?"
        return endpoint, ep_params

    def _parse_result(
        self, result: list[Result], start: datetime, end: datetime, measurement: str
    ) -> list[Dict]:
        # unpack to return specified measurement
        # since TidesAndCurrents returns 1 product per endpoint:
        # -> minimal parsing, just unpack Json
        # details here: https://api.tidesandcurrents.noaa.gov/api/prod/responseHelp.html
        #
        if len(result) > 1:
            raise SeaStateException(
                "TidesAndCurrentsApi doesn't support multiple results"
            )
        try:
            parse_key = self._build_parse_key(measurement)
            if result[0].data.get("error"):
                self._logger.error("TidesAndCurrentsApi error, returning empty data")
                self._logger.error(f"{measurement}:{result[0].data}")
                return []
            data = result[0].data[parse_key]
        except KeyError as e:
            self._logger.exception(result.data)
            raise SeaStateException("TidesAndCurrentsApi unpacking error") from e

        if len(data) == 0:
            self._logger.warning(
                f"No {measurement} data recovered for daterange:\
                    {str(start.date())} : {str(end.date())}"
            )

        return data


if __name__ == "__main__":
    api = TidesAndCurrentsApi()
    result = api.hourly("wind", 9410230, datetime.today(), datetime.today())
    print(result)
    result = api.hourly(9410230, datetime.today(), datetime.today(), "air_temp")
    result = api.hourly(9410230, datetime.today(), datetime.today(), "water_temp")
