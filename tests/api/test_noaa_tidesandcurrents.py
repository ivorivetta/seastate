from seastate.api.noaa_tidesandcurrents import TidesAndCurrentsApi


class TestTidesAndCurrentsApi:
    def test_id(self):
        assert TidesAndCurrentsApi().id == "noaa_tidesandcurrents"
