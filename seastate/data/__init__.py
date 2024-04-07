import glob
import os
from typing import List

from seastate.data.parsers import StationParser
from seastate.models import Station
from seastate.settings import DATASOURCES
from functools import lru_cache


def save_stations() -> None:
    """Calls implemented parsers and writes result to json"""
    parser = StationParser()
    basedir = os.path.dirname(__file__)

    for datasource in DATASOURCES:
        with open(os.path.join(basedir, f"{datasource}.json"), "w") as outfile:
            stations = getattr(parser, datasource)()
            data = parser.to_jsons(stations)
            outfile.write(data)


@lru_cache(maxsize=None)
def load_stations() -> List[Station]:
    """for all *.json in this directory, load into list of Station objects"""
    data = []
    for file in glob.glob(os.path.join(os.path.dirname(__file__), "*.json")):
        with open(file, "r") as content:
            data += StationParser.from_jsons(content.read())
    return data


if __name__ == "__main__":
    # write stations when called from CLI
    save_stations()
else:
    # load stations when imported
    STATIONS = load_stations()
