from seastate.utils import haversine


def test_haversine_success():
    """Test haversine distance calculation"""
    assert haversine(32, -117, 32, -117) == 0
    assert haversine(32, -117, 33, -118) == 145.36863376095982
