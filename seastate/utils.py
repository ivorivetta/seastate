import numpy as np


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns distance in km using haversine method

    Args:
        lat1 (float): Coordinate in decimal degrees
        lon1 (float): Coordinate in decimal degrees
        lat2 (float): Coordinate in decimal degrees
        lon2 (float): Coordinate in decimal degrees

    Returns:
        float: Returns great circle distance in km
    """
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Calculate deltas
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine method for measuring distance on a sphere
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    km = 6367 * c
    return km
