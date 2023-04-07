import api
import googlemaps
import polyline
from pprint import pprint
from places import get_nearby_places
import csv
import os
import random

# TEST
TEST_ORIGIN = '48 Massachusetts Ave w16, Cambridge, MA 02139'
TEST_DESTINATION = '2010 William J Day Blvd, Boston, MA 02127'
NY_DESTINATION = 'City Park Hall, New York, NY 10007'

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
    for i, waypoint in enumerate(waypoints[::increment]):
        locations = get_nearby_places(page_token="",location=waypoint,radius=100000,exclude_types=[],types=['tourist_attraction'])
        print(f'{len(locations)} for waypoint: {i}')
        for location in locations:
            if location.position not in detour_positions:
                detour_positions.add(location.position)
                detours.add(location)
    return detours

# def get_reviews(detours):
#     gmaps = googlemaps.Client(key=api.get_api_key())

#     # for detour_id in detours:
#     #     content = gmaps.place(
#     #         place_id='ChIJ-SCVle9544kRt47b6znsdQM'
#     #     )
#     #     pprint(content)
#     location = (42.3581083, -71.0948251)
#     nearby = get_nearby_places(page_token="",location=location,radius=100000,exclude_types=[],types=['tourist_attraction'])
#     for near in nearby: print(near.name)
#     # pprint(gmaps.places(
#     #     query='Great Dome, 10, Memorial Drive, Cambridge, MA'
#     # ))


if __name__ == '__main__':
    # print(sys.version)
    overview_polyline, distance = get_polyline(destination=NY_DESTINATION)
    # print(polyline)
    waypoints = get_waypoints(overview_polyline)

    # print(len(waypoints), distance)
    detours = possible_detours(waypoints, distance, increment=1)
    with open('test_plot.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'lat', 'long'])
        
        for place_index, place in enumerate(detours):
            # print(place_index)
            # pprint(str(place), width=1000)
            # pprint(place.get_gmaps_link())
            place_lat, place_long = place.position
            place_name = place.name
            writer.writerow([place_name, place_lat, place_long])
    
    with open('test_plot.csv', newline='\n', encoding='utf-8') as csvfile:
        random_detours = csv.reader(csvfile)
        row_list = []
        for row in random_detours:
            row_list.append(row)
        random_detours = random.choices(row_list, k=30)
    
    with open('test_random.csv', 'w+', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'lat', 'long'])
        for row in random_detours:
            writer.writerow(row)
        
        # for place_index, place in enumerate(random_detours):
        #     # print(place_index)
        #     # pprint(str(place), width=1000)
        #     # pprint(place.get_gmaps_link())
        #     place_lat, place_long = place.position
        #     place_name = place.name
        #     writer.writerow([place_name, place_lat, place_long])

    # get_reviews([1])