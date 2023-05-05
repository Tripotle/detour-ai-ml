from typing import List
from data_collection.data_collection_types import Location, Position
from data_collection.places import get_location_by_id
from data_collection.directions import get_detours


def get_locations(origin: str, destination: str) -> List[Location]:
    """
    Given an origin and a destination, return a list of possible detour locations.

    :param origin: the Google Maps Places id of the origin
    :param destination: the Google Maps Places id of the destination
    :return: see above
    """
    origin = get_location_by_id(origin).position
    destination = get_location_by_id(destination).position
    return get_detours(origin, destination)


if __name__ == '__main__':
    # Strictly for testing only
    from pprint import pprint

    TEST_ORIGIN = 'ChIJOwg_06VPwokRYv534QaPC8g'  # MIT
    TEST_DESTINATION = 'ChIJLw8wo4Vw44kRWkWR0c03LH4'  # Boston City Hall
    result = get_locations(TEST_ORIGIN, TEST_DESTINATION)
    pprint(f"total locations: {len(result)}")
    pprint(result)
