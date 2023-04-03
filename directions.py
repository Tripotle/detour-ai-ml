import api
import googlemaps
import polyline
from pprint import pprint
from places import get_nearby_places

# TEST
TEST_ORIGIN = '48 Massachusetts Ave w16, Cambridge, MA 02139'
TEST_DESTINATION = '2010 William J Day Blvd, Boston, MA 02127'

Position = tuple[float, float] # [lat, long]

def get_polyline(origin=TEST_ORIGIN, destination=TEST_DESTINATION):
    gmaps = googlemaps.Client(key=api.get_api_key())
    
    try: 
        query_result: list = gmaps.directions(
            origin=origin,
            destination=destination,
        )
        overview_polyline = query_result[0]['overview_polyline']['points']
        return overview_polyline
    except googlemaps.exceptions.ApiError as e:
        print(origin, destination)
        print("API Error!")
        raise e

def get_waypoints(overview_polyline):
    waypoints = polyline.decode(overview_polyline)
    return waypoints

def possible_detours(waypoints):
    detours = set()
    for waypoint in waypoints[::10]:
        for location in get_nearby_places(page_token="",location=waypoint,radius=5000):
            detours.add(location)
    
    return detours

if __name__ == '__main__':
    # print(sys.version)
    overview_polyline = get_polyline()
    waypoints = get_waypoints(overview_polyline)
    detours = possible_detours(waypoints)
    print(detours)