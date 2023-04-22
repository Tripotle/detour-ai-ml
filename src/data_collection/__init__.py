import urllib.parse
from typing import List
from data_collection.types import Location, Position
from data_collection.directions import get_detours


def get_locations(origin: str, destination: str) -> List[Location]:
    """
    Given an origin and a destination, return a list of possible detour locations.

    :param origin: the Google Maps Places id of the origin
    :param destination: the Google Maps Places id of the destination
    :return: see above
    """
    return get_detours(origin, destination)
