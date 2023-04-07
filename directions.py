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
        distance = query_result[0]['legs'][0]['distance']['value']
        return overview_polyline, distance
    
    except googlemaps.exceptions.ApiError as e:
        print(origin, destination)
        print("API Error!")
        raise e

def get_waypoints(overview_polyline):
    waypoints = polyline.decode(overview_polyline)
    return waypoints

def possible_detours(waypoints, distance, increment=20):
    detours = set()
    detour_positions = set()
    for waypoint in waypoints[::increment]:
        for location in get_nearby_places(page_token="",location=waypoint,radius=20000):
            if location.position not in detour_positions:
                detour_positions.add(location.position)
                detours.add(location)
    return detours

def get_reviews(detours):
    gmaps = googlemaps.Client(key=api.get_api_key())

    for detour_id in detours:
        content = gmaps.place(
            place_id='ChIJ-SCVle9544kRt47b6znsdQM'
        )
        pprint(content)

if __name__ == '__main__':
    # print(sys.version)
    overview_polyline, distance = get_polyline()
    waypoints = get_waypoints(overview_polyline)
    # print(len(waypoints), distance)
    detours = possible_detours(waypoints, distance, increment=50)
    for place_index, place in enumerate(detours):
        print(place_index)
        pprint(str(place), width=1000)
        pprint(place.get_gmaps_link())
    # get_reviews([1])