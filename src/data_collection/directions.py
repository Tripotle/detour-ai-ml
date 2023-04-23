import api
from data_collection.places import *
import csv
import random
from math import radians, cos
import numpy as np
import googlemaps
import polyline
import threading
from pprint import pprint

# TEST LOCATIONS
TEST_ORIGIN = '48 Massachusetts Ave w16, Cambridge, MA 02139'
TEST_DESTINATION = '2010 William J Day Blvd, Boston, MA 02127'
NY_DESTINATION = 'City Park Hall, New York, NY 10007'


# MATHEMATICAL CONVERSIONS
DEG_LAT_TO_M = 110574
DEG_LONG_TO_M = 111320
MAX_SEARCH_RADIUS = 35355 # 50000/sqrt(2)


def get_waypoints(origin, destination):
    gmaps = googlemaps.Client(key=api.get_google_api_key())
    
    try: 
        query_result: list = gmaps.directions(
            origin=origin,
            destination=destination,
        )
        
        # overview_polyline = query_result[0]['overview_polyline']['points']
        # waypoints = polyline.decode(overview_polyline)
        distance = query_result[0]['legs'][0]['distance']['value']
        origin_position = query_result[0]['legs'][0]['start_location']
        olat, olong = origin_position['lat'], origin_position['lng']
        destination_position = query_result[0]['legs'][0]['end_location']
        dlat, dlong = destination_position['lat'], destination_position['lng']
        
        alat, along = (olat+dlat)/2, (olong+dlong)/2
        route_radius = distance/2
        print(olat, olong)
        print(dlat, dlong)
        print(alat, along, route_radius)

        # forming search box
        lat_diff = route_radius/DEG_LAT_TO_M
        long_diff = route_radius/(DEG_LONG_TO_M*cos(radians(alat)))
        print(lat_diff, long_diff)
        sb_minlat, sb_maxlat = alat-lat_diff, alat+lat_diff
        sb_minlong, sb_maxlong = along-long_diff, along+long_diff

        waypoints = []
        for waypoint_lat in np.arange(sb_minlat, sb_maxlat, MAX_SEARCH_RADIUS/DEG_LAT_TO_M):
            deg_long_to_m = DEG_LONG_TO_M*cos(radians(waypoint_lat))
            for waypoint_long in np.arange(sb_minlong, sb_maxlong, MAX_SEARCH_RADIUS/deg_long_to_m):
                waypoints.append((waypoint_lat, waypoint_long))

        return waypoints, distance
    
    except googlemaps.exceptions.ApiError as e:
        print(origin, destination)
        print("API Error!")
        raise e


def possible_detours(waypoints, distance, increment=1):
    detours = set()
    detour_positions = set()
    threads = []
    locations = []

    def get_nearby_places_multithread(waypoint, locations, index):
        locations += get_nearby_places(
            page_token="",
            location=waypoint,
            radius=50000,
            exclude_types=[],
            types=['tourist_attraction']
        )

    for i, waypoint in enumerate(waypoints[::increment]):
        threads.append(threading.Thread(
            target=get_nearby_places_multithread, 
            args=(waypoint, locations, i)
        ))
        threads[i].start()
        print(f'waypoint {i} was processed')
        # need to eventually adjust increment based on distance (or radius or both)
    
    for thread in threads:
        thread.join()

    for location in locations:
        if location.position not in detour_positions:
            detour_positions.add(location.position)
            detours.add(location)
    
    # print(detours)
    return detours


def get_reviews(detours):
    gmaps = googlemaps.Client(key=api.get_google_api_key())
    detours_with_reviews = []
    threads = []
    detours_with_reviews = []

    def get_reviews_multithread(detour):
        query_result: dict = gmaps.place(
                place_id=detour.place_id
            )
        detour_results = query_result['result']
        if 'reviews' in detour_results.keys():
            detour_reviews = detour_results['reviews']
            for detour_review in detour_reviews:
                if detour_review['text']: detour.information.append(detour_review['text'])
            if detour.information: detours_with_reviews.append(detour)
        
    for i, detour in enumerate(list(detours)):
        threads.append(threading.Thread(
            target=get_reviews_multithread, 
            args=(detour,)
        ))
        threads[i].start()
        print(f'detour {i} was processed')
    
    for thread in threads:
        thread.join()
    
    return detours_with_reviews

def get_detours(origin, destination, increment=1):
    waypoints, distance = get_waypoints(origin=origin, destination=destination)
    detours = possible_detours(waypoints=waypoints, distance=distance, increment=increment)
    detours_with_reviews = get_reviews(detours)
    
    return list(detours_with_reviews)

if __name__ == '__main__':
    # print("Success!")
    # gmaps = googlemaps.Client(key=api.get_api_key())
    # place = gmaps.find_place(
    #     input='Samuel H. Young Park',
    #     input_type='textquery',
    # )
    # place = gmaps.place(
    #             place_id=place['candidates'][0]['place_id'] #'ChIJ4bwEPIBw44kRs7STmn977tE'
    #         )
    # place_results = place['result']
    # test = []
    # if 'reviews' in place_results.keys():
    #     detour_reviews = place_results['reviews']
    #     for detour_review in detour_reviews:
    #         if detour_review['text']: test.append(detour_review['text'])
    # print(test)

    detours = get_detours(TEST_ORIGIN, TEST_DESTINATION, 1)
    for detour_index, detour in enumerate(detours):
        print(detour_index)
        pprint(str(detour), width=1000)
        print(detour.information)
        pprint(detour.get_gmaps_link())

    # with open('out/test_plot.csv', 'w', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['name', 'lat', 'long'])
        
    #     for place_index, place in enumerate(detours):
    #         place_lat, place_long = place.position
    #         place_name = place.name
    #         writer.writerow([place_name, place_lat, place_long])
    
    # with open('out/test_plot.csv', newline='\n', encoding='utf-8') as csvfile:
    #     random_detours = csv.reader(csvfile)
    #     row_list = []
    #     for row in random_detours:
    #         row_list.append(row)
    #     random_detours = random.choices(row_list, k=30)
    
    # with open('out/test_plot.csv', 'w+', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['name', 'lat', 'long'])
    #     for row in random_detours:
    #         writer.writerow(row)