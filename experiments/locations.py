from src import api
import googlemaps
from pprint import pprint

# Kresge
TEST_ADDRESS = '48 Massachusetts Ave w16, Cambridge, MA 02139'


def test_api(address=TEST_ADDRESS):
    gmaps = googlemaps.Client(key=api.get_api_key())

    try:
        place = gmaps.find_place(
            "park",
            "textquery",
            fields=["geometry/location", "place_id"],
            location_bias="point:90,90",
        )
        pprint(place)
    except googlemaps.exceptions.ApiError as e:
        pprint(e)

    # https://developers.google.com/maps/documentation/javascript/geocoding#GeocodingRequests
    try:
        result = gmaps.geocode(address)
        pprint(result)
    except googlemaps.exceptions.ApiError as e:
        pprint(e)


if __name__ == '__main__':
    print(f'api key is {api.get_api_key()}')
    test_api()
