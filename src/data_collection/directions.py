import api
from data_collection.places import *
import googlemaps
from google.cloud import firestore
import polyline
import wikipediaapi
from math import radians, sin, cos, acos
import numpy as np
import threading
import time
from pprint import pprint
import csv
import random
import os

# TEST LOCATIONS
TEST_ORIGIN = '48 Massachusetts Ave w16, Cambridge, MA 02139'
CLOSE_DESTINATION = '455 Main St, Worcester, MA 01608'
TEST_DESTINATION = '2010 William J Day Blvd, Boston, MA 02127'
NY_DESTINATION = 'City Park Hall, New York, NY 10007'


# MATHEMATICAL CONVERSIONS
DEG_LAT_TO_M = 110574
DEG_LONG_TO_M = 111320
MAX_SEARCH_RADIUS = 35355 # 50000/sqrt(2)
EARTH_RADIUS = 6371000


# API LIMIT
MAX_REQUESTS_PER_SECOND = 90


def calculate_distance(position1: Position, position2: Position) -> float:
    p1_lat, p1_long = position1
    p2_lat, p2_long = position2
    p1_lat = radians(90-p1_lat)
    p2_lat = radians(90-p2_lat)
    # print(EARTH_RADIUS * acos(cos(p1_lat)*cos(p2_lat) + sin(p1_lat)*sin(p2_lat)*cos(radians(p2_long-p1_long))))
    return EARTH_RADIUS * acos(cos(p1_lat)*cos(p2_lat) + sin(p1_lat)*sin(p2_lat)*cos(radians(p2_long-p1_long)))


def position_filter(origin: Position, destination: Position, detour: Position) -> bool:
    # returns True if we should keep filter
    olat, olong = origin
    dlat, dlong = destination
    detour_lat, detour_long = detour
    
    within_lat = olat < detour_lat < dlat or dlat < detour_lat < olat
    within_long = olong < detour_long < dlong or dlong < detour_long < olong

    return (within_lat or within_long)


def get_wikipedia_review(detour: Location) -> Location | None:
    # this might be buggy...test with longer routes!
    wiki = wikipediaapi.Wikipedia('en')
    page = wiki.page(detour.name)
    
    if page.exists() and "may refer to" not in page.summary: 
        detour.information.append(page.summary)
    
    return detour if detour.information else None


db = firestore.Client(project='plated-mantra-385005')

def store_location(detour: Location) -> None:
    doc_ref = db.collection(u'detours').document(detour.place_id)
    doc_ref.set({
        'place_id': detour.place_id,
        'information': detour.information,
    })
    # print(f"store-location was called for {detour.name}")


def fetch_location(detour: Location) -> Location | None:
    # db = firestore.Client(project='plated-mantra-385005')
    doc_ref = db.collection(u'detours').document(detour.place_id)
    doc = doc_ref.get()
    
    if doc.exists:
        detour_doc = doc.to_dict()
        detour.information += detour_doc['information']
        # print(f"location was successfully fetched for {detour.name}")
        return detour
    else:
        # print(f"doc was not found for {detour.name}")
        return None



def get_waypoints(origin: str | Position, destination: str | Position, max_distance: float | None = None) -> tuple[List[Position], Position, Position, float]:
    gmaps = googlemaps.Client(key=api.get_google_api_key())
    
    try: 
        query_result: list = gmaps.directions(
            origin=origin,
            destination=destination,
        )
        
        # origin (o) and destination (d) positions
        origin_position = query_result[0]['legs'][0]['start_location']
        olat, olong = origin_position['lat'], origin_position['lng']
        origin_pos = (olat, olong)
        destination_position = query_result[0]['legs'][0]['end_location']
        dlat, dlong = destination_position['lat'], destination_position['lng']
        dest_pos = (dlat, dlong)

        # overview_polyline = query_result[0]['overview_polyline']['points']
        # waypoints = polyline.decode(overview_polyline)
        route_distance = query_result[0]['legs'][0]['distance']['value']
        geodesic_distance = calculate_distance(origin_pos, dest_pos)
        if max_distance == None: max_distance = 1.2*geodesic_distance # 1.2 is quite arbitrary, could change to user input later

        # the method below currently does not work for shorter distances, so revert to old method
        # if route_distance < 60000:
        #     overview_polyline = query_result[0]['overview_polyline']['points']
        #     waypoints = polyline.decode(overview_polyline)
        #     waypoint_increment = len(waypoints) // 50 if len(waypoints) > 50 else 1
        #     return waypoints[::waypoint_increment], origin_pos, dest_pos, float(route_distance)
        
        # new method of calculating waypoints
        # center/average (a) latitude and longitude
        alat, along = (olat+dlat)/2, (olong+dlong)/2
        route_radius = route_distance/2

        # forming search box (sb)
        lat_diff = route_radius/DEG_LAT_TO_M
        long_diff = route_radius/(DEG_LONG_TO_M*cos(radians(alat)))
        sb_minlat, sb_maxlat = alat-lat_diff, alat+lat_diff
        sb_minlong, sb_maxlong = along-long_diff, along+long_diff

        waypoints = []
        for waypoint_lat in np.arange(sb_minlat, sb_maxlat, min(lat_diff/3, MAX_SEARCH_RADIUS/DEG_LAT_TO_M)): # up to 2*3 = 6 points in grid latitude-wise
            deg_long_to_m = DEG_LONG_TO_M*cos(radians(waypoint_lat))
            for waypoint_long in np.arange(sb_minlong, sb_maxlong, min(long_diff/3, MAX_SEARCH_RADIUS/deg_long_to_m)): #  up to 2*3 = 6 points in grid longitude-wise
                waypoint_pos = (waypoint_lat, waypoint_long)
                if not position_filter(origin_pos, dest_pos, waypoint_pos): continue
                if calculate_distance(origin_pos, waypoint_pos) + calculate_distance(dest_pos, waypoint_pos) < max_distance:
                    waypoints.append((waypoint_lat, waypoint_long))

        return waypoints, origin_pos, dest_pos, float(geodesic_distance)
    
    except googlemaps.exceptions.ApiError as e:
        print(origin, destination)
        print("API Error!")
        raise e


def possible_detours(waypoints: List[Position], origin: Position, destination: Position, increment=1) -> List[Location]:
    detours = set()
    detour_positions = set()
    threads = []
    locations = []

    def get_nearby_places_multithread(waypoint, locations):
        locations += get_nearby_places(
            page_token="",
            location=waypoint,
            # radius=50000,
            # exclude_types=[],
            types=['tourist_attraction']
        )
        
    for i, waypoint in enumerate(waypoints[::increment]):
        threads.append(threading.Thread(
            target=get_nearby_places_multithread, 
            args=(waypoint, locations)
        ))
        threads[i].start()
        # prevents more than 100 requests per second
        if (i+1) % MAX_REQUESTS_PER_SECOND == 0: 
            print("slept on waypoint call")
            time.sleep(1)
    
    for thread in threads:
        thread.join()

    for location in locations:
        if not position_filter(origin, destination, location.position):
            continue
        if location.position not in detour_positions:
            detour_positions.add(location.position)
            detours.add(location)
    
    # print(detours)
    return list(detours)


def get_reviews(detours: List[Location]):
    detours_with_reviews = []
    threads = []
    detours_with_reviews = []

    def get_reviews_multithread(detour):
        detour_with_review = fetch_location(detour)
        if detour_with_review: # location in database
            detours_with_reviews.append(detour_with_review)
        else:
            detour_with_review = get_place_reviews(detour)
            detour_with_review = get_wikipedia_review(detour)
            if detour_with_review: 
                store_location(detour_with_review)
                detours_with_reviews.append(detour_with_review)
    
    def do_nothing(detour):
        pass # testing multithreading

    for i, detour in enumerate(detours):
        threads.append(threading.Thread(
            target=get_reviews_multithread, 
            args=(detour,)
        ))
        threads[i].start()
        if (i+1) % MAX_REQUESTS_PER_SECOND == 0: 
            print("slept on review call")
            time.sleep(1)
    
    for thread in threads:
        thread.join()

    return detours_with_reviews


def get_detours(origin: str | Position, destination: str | Position, increment=1) -> List[Location]:
    waypoints, origin_pos, dest_pos, geodesic_distance = get_waypoints(origin=origin, destination=destination)
    detours = possible_detours(waypoints=waypoints, origin=origin_pos, destination=dest_pos, increment=increment)
    
    start = time.time()
    detours_with_reviews = get_reviews(detours)
    print(time.time() - start, "seconds to obtain reviews")

    for detour in detours_with_reviews: # for distance weighting (although this probably only works on contiguous land)
        detour.distance_from_route = geodesic_distance/(calculate_distance(origin_pos, detour.position) + calculate_distance(detour.position, dest_pos))
    
    return list(detours_with_reviews)


if __name__ == "__main__":
    detours = get_detours(TEST_ORIGIN, CLOSE_DESTINATION, 1)
    # for detour in detours:
    #     fetch_location(detour)