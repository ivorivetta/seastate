from seastate.api.rest_adapter import RestAdapter
from seastate.models import Result
from seastate.exceptions import SeaStateException

import pytest


# needs fixture for adapter
class TestRestAdapter:
    @pytest.fixture
    def adapter(self):
        return RestAdapter("google.com")

    # _do
    def test__do_good_request_returns_result(self, adapter):
        result = adapter._do("GET", "robots.txt")
        assert isinstance(result, Result)

    @pytest.mark.skip
    def test__do_bad_json_raises_SeaStateException(self, adapter):
        result = adapter._do("GET", "")  # returning htnl counts as bad json
        assert isinstance(result, SeaStateException)
