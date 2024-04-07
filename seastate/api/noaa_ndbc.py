import logging
from datetime import datetime, timedelta
from typing import Dict, Union

from seastate.api.base import BaseApi
from seastate.api.rest_adapter import RestAdapter
from seastate.exceptions import SeaStateException
from seastate.models import Result


class NdbcApi(BaseApi):
    def __init__(self, logger: logging.Logger = None):
        """Constructor for NdbcApi, composed with RestAdapter"""
        self._logger = logger or logging.getLogger(__name__)
        self._adapter = RestAdapter("www.ndbc.noaa.gov")

    def _build_parse_key(self, measurement: str = None) -> Union[str, list[str], None]:
        measurement = measurement.lower()
        if "tide" in measurement:
            key = ["TIDE"]
        elif "wind" in measurement:
            key = ["WSPD", "SPD"]
            # additional wind information handled when unpacking
        elif "water_temp" in measurement:
            key = ["WTMP"]
        elif "air_temp" in measurement:
            key = ["ATMP"]
        elif "air_press" in measurement:
            key = ["PRES", "BARO", "BAR"]
        elif "wave" in measurement:
            key = ["WVHT", "H0"]
            # additional swell information handled when unpacking
        elif "conductivity" in measurement:
            raise SeaStateException(
                "Unsupported measurement requested, please report issue"
            )
        else:
            raise SeaStateException(
                "Unsupported measurement requested, please report issue"
            )
        return key

    def _build_endpoint(
        self, measurement: str, station_id: str, start: datetime, end: datetime
    ) -> (str, Dict):
        # Collect endpoints needed to cover daterange
        endpoints = []
        # daterange spans realtime endpoint (45 days)
        archive_cutoff_date = datetime.today() - timedelta(days=45)
        if start > archive_cutoff_date or end > archive_cutoff_date:
            # "realtime" endpoint covers prev 45 days
            endpoints += [f"data/realtime2/{station_id}.txt"]
        # daterange spans archive, for current year
        # cutoff month has a unique endpoint
        if start < archive_cutoff_date < end:
            requested_months = [archive_cutoff_date.strftime("%b")]
            endpoints += [f"data/stdmet/{x}/{station_id}.txt" for x in requested_months]
        # within current year, endpoints are grouped by month
        if start < archive_cutoff_date and end.year == datetime.today().year:
            # use January if start year precedes the archive cutoff year
            # else use start month
            start_range = 1 if start.year < archive_cutoff_date.year else start.month
            # end of range will be up to cutoff
            # duplicates to be filtered downstream
            end_range = archive_cutoff_date.month
            # Endpoint uses month number and abbreviated month designations (%b)
            requested_months = [
                (str(x), datetime(1, x, 1).strftime("%b"))
                for x in range(start_range, end_range)
            ]
            endpoints += [
                f"view_text_file.php?filename= \
                    {station_id}{x}{datetime.today().year} \
                        .txt.gz&dir=data/stdmet/{y}/"
                for x, y in requested_months
            ]
        # daterange spans prior years
        #
        if start < archive_cutoff_date and start.year < datetime.today().year:
            # if end year is this year, handled upstream
            # else, it is a prior year and needs to be included
            end_range = end.year if end.year == datetime.today().year else end.year + 1
            requested_years = [str(x) for x in range(start.year, end_range)]
            endpoints += [
                f"view_text_file.php?filename= \
                    {station_id}h{x} \
                        .txt.gz&dir=data/historical/stdmet/"
                for x in requested_years
            ]
        return endpoints, None

    def _parse_result(
        self, result: list[Result], start: datetime, end: datetime, measurement: str
    ) -> list[Dict]:
        # unpack list of results to text
        tmp = ""
        for res in result:
            tmp += res.data

        # unpack text result
        # realtime ndbc reports are a text file with previous 45 days of measurements
        # archival are a years worth
        # todo: unpack text file into t: and v:
        data = []
        for i, value in enumerate(tmp.split("\n")):
            # turn str to list
            # known anomaly: 2 space characters sometimes delimiting
            line = value.replace("  ", " ").split(" ")
            while " " in line:
                line.remove(" ")  # remove blanks
            while "" in line:
                line.remove("")  # remove blanks

            # handle corrupted lines
            if len(line) == 0:
                self._logger.info(f"ignoring line #{i}:{str(line)}")
                continue

            # handle header lines
            if line[0] in ["#YY", "YY"]:
                # header row starts with #YY in realtime, YY in archive
                header = line
                # strip '#' from '#YY'
                header[0] = header[0].strip("#")
                continue
            elif line[0] in ["#yr"]:
                # skipping units line
                continue

            # ignore lines outside of daterange
            # archive files sometimes use 95 instead of 1995
            if not (start.year <= int(line[0]) <= end.year) and not (
                abs(start.year % 100) <= int(line[0]) <= abs(end.year % 100)
            ):
                # 4 digit year representation
                continue
            if not start.month <= int(line[1]) <= end.month:
                continue
            if not start.day <= int(line[2]) <= end.day:
                continue

            # line is in requested daterange
            # parse timestamp
            timestamp = datetime(
                year=int(
                    line[0] if len(line[0]) == 4 else "19" + line[0]
                ),  # rebuild dates with archive format
                month=int(line[1]),
                day=int(line[2]),
                hour=int(line[3]),
                minute=int(
                    line[4] if "mm" in header else 0
                ),  # archival format is hourly
            ).isoformat(sep=" ")
            # parse measurement column
            # because of changes in the source api column names over the years
            # we try to unpack with the possible variants
            # details here: https://www.ndbc.noaa.gov/measdes.shtml
            temp_data = {}
            # unpack time and main value
            for key in self._build_parse_key(measurement):
                try:
                    temp_data["t"] = timestamp
                    temp_data["v"] = line[header.index(key)]
                except (KeyError, ValueError):
                    pass
            # check for success before continuing
            if len(temp_data) < 2:
                self._logger.error(value)
                raise SeaStateException("NdbcApi unpacking error, please report issue")
            # wind sometimes has direction and gust data
            if "wind" in measurement:
                # for wind direction:
                for key in ["WDIR", "WD", "DIR"]:
                    try:
                        temp = line[header.index(key)]
                        temp_data["d"] = (
                            temp
                            if temp and "999" not in temp and "MM" not in temp
                            else None
                        )  # 999 for direction
                    except Exception as e:
                        self._logger.debug(f"{e} for {measurement}")
                # For wind gust:
                for key in ["GST", "GSP"]:
                    try:
                        temp = line[header.index(key)]
                        temp_data["g"] = (
                            temp
                            if temp and "99" not in temp and "MM" not in temp
                            else None
                        )  # 99 for decimal
                    except Exception as e:
                        self._logger.debug(f"{e} for {measurement}")
            # wave sometimes has period and direction
            if "wave" in measurement:
                # for dominant wave period:
                for key in ["DPD", "DOMPD"]:
                    try:
                        temp = line[header.index(key)]
                        temp_data["dpd"] = (
                            temp
                            if temp and "99" not in temp and "MM" not in temp
                            else None
                        )  # 99 for decimal
                    except Exception as e:
                        self._logger.debug(f"{e} for {measurement}")
                # For dominant wave direction:
                for key in ["MWD"]:
                    try:
                        temp = line[header.index(key)]
                        temp_data["mwd"] = (
                            temp
                            if temp and "999" not in temp and "MM" not in temp
                            else None
                        )  # 999 for direction
                    except Exception as e:
                        self._logger.debug(f"{e} for {measurement}")
                # For average wave period
                for key in ["APD", "AVP"]:
                    try:
                        temp = line[header.index(key)]
                        temp_data["apd"] = (
                            temp
                            if temp and "99" not in temp and "MM" not in temp
                            else None
                        )
                    except Exception as e:
                        self._logger.debug(f"{e} for {measurement}")
            data.append(temp_data)

        # log warning if no data recovered for daterange
        if len(data) == 0:
            self._logger.warning(
                f"No {measurement} data recovered for daterange:\
                    {str(start.date())} : {str(end.date())}"
            )

        # todo: scrub duplicates between cutoff month and realtime
        return data


if __name__ == "__main__":
    api = NdbcApi()
    # check daterange within realtime
    # result = api.hourly(
    #     "wind",
    #     46224,
    #     datetime.today(),
    #     datetime.today() - timedelta(days=2),
    # )

    # check daterange for request only in prior years
    # result = api.hourly(
    #     "wind",
    #     46224,
    #     datetime.today() - timedelta(days=2 * 365 + 30),
    #     datetime.today() - timedelta(days=1 * 365 + 30),
    # )

    # check daterange spanning archive and realtime, into prior year
    # result = api.hourly(
    #     "wind",
    #     46224,
    #     datetime.today() - timedelta(days=365 + 30),
    #     datetime.today(),
    # )

    # check old archive with different headers
    # check date format
    result = api.hourly(
        "air_press",
        42040,
        datetime(1996, 2, 1),
        datetime(1996, 2, 2),
    )
