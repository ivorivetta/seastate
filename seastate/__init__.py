import logging
from datetime import datetime, timedelta
from typing import Dict, Union

from seastate.api.api_mediator import ApiMediator
from seastate.settings import MEASUREMENTS


class SeaState:
    def __init__(
        self, lat: float, lon: float, exclude: list = [], logger: logging.Logger = None
    ):
        self._logger = logger or logging.getLogger(__name__)
        self.lat = float(lat)
        self.lon = float(lon)
        self.exclude = list(exclude)
        self.mediator_map = {}
        self._set_api_mediators()

    @property
    def _requested_measurements(self) -> tuple:
        return (x for x in MEASUREMENTS if x not in self.exclude)

    def _build_date_range(
        self, start: Union[datetime, None], end: Union[datetime, timedelta, None]
    ) -> tuple[datetime, datetime]:
        """
        Builds date range to fullest days possible,
        with start and end at midnight and (midnight - 1)
        """
        # Process timeframe
        # todo: handle iso date strings
        # todo: handle bad date strings
        if start and end:  # all values provided
            # end can be declared relative to start as a timedelta
            if isinstance(end, timedelta):
                end = start + end
        elif start and not end:  # no end provided, return same day as start
            end = start
        elif not start and not end:  # nothing provided, return today
            start = end = datetime.today()

        # remove microseconds to pass comparison tests
        # remove hours and minutes from start
        # set hours and minutes to end of day for end
        if isinstance(start, datetime):
            start = start.replace(microsecond=0)
            start = start.replace(hour=0, minute=0, second=0)
        if isinstance(end, datetime):
            end = end.replace(microsecond=0)
            end = end.replace(hour=23, minute=59, second=59)

        # log warning if end is before start
        if end < start:
            self._logger.warning("end is after start")

        return start, end

    def _get_mediator(self, measurement: str) -> ApiMediator:
        return self.__getattribute__(measurement)

    def _set_mediator(self, measurement: str) -> None:
        if measurement in self.exclude:
            self.__setattr__(measurement, None)
        else:
            tmp = ApiMediator(measurement, self.lat, self.lon, self.exclude)
            # add attribute
            self.__setattr__(measurement, tmp)
            # register mediator to map
            self.mediator_map[measurement] = tmp

    def _set_api_mediators(self) -> None:
        """set APIMediator as attribute for all implemented measurements"""
        for measurement in MEASUREMENTS:
            self._set_mediator(measurement)

    def _get_data(self, key: str, start: datetime, end: datetime) -> list[Dict]:
        mediator = self._get_mediator(key)
        data = {}
        data = mediator.api.measurement_from_date_range(
            measurement=mediator.measurement,
            station_id=mediator.station.id,
            start=start,
            end=end,
        )
        return data

    def from_date_range(
        self,
        start: Union[datetime, None] = None,
        end: Union[datetime, timedelta, None] = None,
    ) -> Dict:
        # process timeframe
        start, end = self._build_date_range(start, end)

        # makes an api call for each measurement,
        # the idea is that the cache absorbs duplicate calls
        # and the actual data is small so it's ok to reprocess
        data = {
            key: self._get_data(key, start, end) for key in self._requested_measurements
        }

        # previously, i manually built a dict with 7 api calls
        # for each measurement
        # get attribute.api
        # call api.from_date_range on measurement, station, start, end
        # gets measurement again
        # gets staion again
        # data = {}
        # for measurement_key in MEASUREMENTS:
        #     # access the configured api to generate response with hourly method
        #     data[measurement_key] = self.__getattribute__(
        #         measurement_key
        #     ).api.measurement_from_date_range(
        #         measurement=self.__getattribute__(measurement_key).measurement,
        #         station_id=self.__getattribute__(measurement_key).station.id,
        #         start=start,
        #         end=end,
        #     )
        return data

    def hourly(
        self,
        start: Union[datetime, None] = None,
        end: Union[datetime, timedelta, None] = None,
    ) -> Dict:
        """Convenience method to return 1 sample per hour for each api"""
        data_all = self.from_date_range(start, end)
        data = {}
        for key in data_all:
            # find the first minute within the hour
            # the apis typically use the same minute
            first_minute = 0
            while datetime.fromisoformat(data_all[key][0]["t"]).minute != first_minute:
                first_minute += 1
                # prevent endless loop
                if first_minute == 60:
                    data[key] = []
                    break
            # keep one reading per hour
            data[key] = [
                x
                for x in data_all[key]
                if datetime.fromisoformat(x["t"]).minute == first_minute
            ]
        return data

    def measurements_from_date_range(
        self, start: datetime = None, end: Union[datetime, timedelta] = None
    ) -> Dict:
        self._logger.warning(
            "measurements_from_date_range() is deprecated,\
                use from_date_range() instead"
        )
        return self.from_date_range(start, end)


if __name__ == "__main__":
    api = SeaState(32, -117)
    start = datetime(2023, 9, 5)
    end = datetime(2023, 9, 5)
    data = api.from_date_range(start, end)
    a = api.hourly(start, end)

    # check daterange within realtime
    # result = api.hourly(datetime.today()-timedelta(days=2),datetime.today())

    # # check daterange for request only in prior years
    # result = api.hourly(
    #     datetime.today() - timedelta(days=2 * 365 + 30),
    #     datetime.today() - timedelta(days=1 * 365 + 30),
    # )

    # # check daterange spanning archive and realtime, into prior year
    # result = api.hourly(datetime.today()-timedelta(days=365+30),datetime.today())

    # # check old archive with different headers
    # # check date format
    # result = api.hourly('air_press',42040,datetime(1996,2,1),datetime(1996,2,2))
