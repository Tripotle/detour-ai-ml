import api
import googlemaps
from pprint import pprint

# Kresge
TEST_ADDRESS = '48 Massachusetts Ave w16, Cambridge, MA 02139'
# can get from geocode API
LOCATION = (42.3581083, -71.0948251)

def test_places_api(location=LOCATION, radius=500):
    gmaps = googlemaps.Client(key=api.get_api_key())
    
    try:
        results = gmaps.places_nearby(
            location,
            radius,
            type=["aquarium", "point_of_interest", "tourist_attraction",]
        )
        pprint(len(results))
    except googlemaps.exceptions.ApiError as e:
        pprint(e)

if __name__ == '__main__':
    print(f'api key is {api.get_api_key()}')
    test_places_api()
