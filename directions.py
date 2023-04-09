import api
from places import get_nearby_places
import csv
import random
import googlemaps
import polyline
import threading
from pprint import pprint

# TEST LOCATIONS
TEST_ORIGIN = '48 Massachusetts Ave w16, Cambridge, MA 02139'
TEST_DESTINATION = '2010 William J Day Blvd, Boston, MA 02127'
NY_DESTINATION = 'City Park Hall, New York, NY 10007'

# Position = tuple[float, float] # [lat, long]

def get_waypoints(origin, destination):
    gmaps = googlemaps.Client(key=api.get_api_key())
    
    try: 
        query_result: list = gmaps.directions(
            origin=origin,
            destination=destination,
        )
        
        overview_polyline = query_result[0]['overview_polyline']['points']
        waypoints = polyline.decode(overview_polyline)
        distance = query_result[0]['legs'][0]['distance']['value']

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
            radius=100000,
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
        # locations = get_nearby_places(
            # page_token="",
            # location=waypoint,
            # radius=100000,
            # exclude_types=[],
            # types=['tourist_attraction']
        # )
        # print(f'{len(locations)} for waypoint: {i}')
    
    for thread in threads:
        thread.join()

    for location in locations:
        if location.position not in detour_positions:
            detour_positions.add(location.position)
            detours.add(location)
    
    # print(detours)
    return detours

def get_reviews(detours):
    gmaps = googlemaps.Client(key=api.get_api_key())
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
    # try:
    #     query_result: dict = gmaps.place(
    #         place_id=detour.place_id
    #     )
        
    #     detour_results = query_result['result']
    #     if 'reviews' in detour_results.keys():
    #         detour_reviews = detour_results['reviews']
    #         for detour_review in detour_reviews:
    #             if detour_review['text']: detour.information.append(detour_review['text'])
    #         if detour.information: detours_with_reviews.append(detour)
    
    # except googlemaps.exceptions.ApiError as e:
    #     print(detour.name, detour.place_id)
    #     print("API Error!")
    #     raise e
    
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

    detours = get_detours(TEST_ORIGIN, TEST_DESTINATION, 30)
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