from seastate.data import load_stations
from seastate.models import Station


def test_load_stations():
    stations = load_stations()
    assert len(stations) > 0
    assert isinstance(stations[0], Station)
