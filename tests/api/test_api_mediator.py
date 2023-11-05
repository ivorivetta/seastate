from seastate.api.api_mediator import ApiMediator
import pytest


class TestApiMediator:
    @pytest.fixture
    def mediator(self):
        return ApiMediator("wind", 32, -117)

    @pytest.mark.skip
    def test_1(self):
        # init
        assert False
