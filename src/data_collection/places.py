from __future__ import annotations
import api
import googlemaps
from pprint import pprint
from data_collection.data_collection_types import Location, Position
import urllib.parse

from typing import List

# Kresge
TEST_ADDRESS = '48 Massachusetts Ave w16, Cambridge, MA 02139'
# can get from geocode API
TEST_LOCATION = (42.3581083, -71.0948251)

# https://developers.google.com/maps/documentation/places/web-service/supported_types
PLACE_TYPES: List[str] = [
    "amusement_park",
    "aquarium",
    "art_gallery",
    "cafe",
    "campground",
    "casino",
    "city_hall",
    "courthouse",
    "embassy",
    "library",
    "museum",
    "park",
    "shopping_mall",
    "stadium",
    "tourist_attraction",
    "university",
    "zoo",
    "landmark",
    "natural_feature",
    "town_square",
    "route",
]

EXCLUDE_PLACE_TYPES: List[str] = [
    "accounting",
    "airport",
    "atm",
    "bank",
    "bus_station",
    "bowling_alley",
    "bus_station",
    "car_dealer",
    "car_rental",
    "car_repair",
    "car_wash",
    "cemetery",
    "clothing_store",
    "convenience_store",
    "dentist",
    "department_store",
    "drugstore",
    "doctor",
    "electrician",
    "electronics_store",
    "fire_station",
    "florist",
    "funeral_home",
    "furniture_store",
    "gas_station",
    "gym",
    "hair_care",
    "hardware_store",
    "hospital",
    "insurance_agency",
    "jewelry_store",
    "laundry",
    "lawyer",
    "light_rail_station",
    "liquor_store",
    "local_government_office",
    "locksmith",
    "lodging",
    "meal_delivery",
    "meal_takeaway",
    "movie_rental",
    "moving_company",
    "painter",
    "parking",
    "pet_store",
    "pharmacy",
    "physiotherapist",
    "plumber",
    "police",
    "post_office",
    "primary_school",
    "real_estate_agency",
    "restaurant",
    "roofing_contractor",
    "rv_park",
    "secondary_school",
    "shoe_store",
    "spa",
    "storage",
    "subway_station",
    "supermarket",
    "taxi_stand",
    "train_station",
    "transit_station",
    "travel_agency",
    "veterinary_care",
    "continent",
    "country",
    "finance",
    "floor",
    "general_contractor",
    "neighborhood",
    "political",
    "post_box",
    "postal_code",
    "postal_code_prefix",
    "postal_code_suffix",
    "postal_town",
    "premise",
    "room",
    "street_address",
    "street_number",
    "sublocality",
]


def from_query_result(query_result: any) -> Location:
    return Location(name=query_result['name'],
                    position=(query_result['geometry']['location']['lat'], query_result['geometry']['location']['lng']),
                    place_id=query_result['place_id'], 
                    types=query_result['types'],
                    rating=float(query_result['rating']) if 'rating' in query_result else 0.0,
                    num_ratings=query_result['user_ratings_total'] if 'user_ratings_total' in query_result else 0,
                    )


def get_location_by_id(id: str) -> Location | None:
    gmaps = googlemaps.Client(key=api.get_google_api_key())
    query_result = gmaps.place(
        place_id=id,
        fields=["name", "geometry", "place_id", "type"]
    )

    return from_query_result(query_result['result'])


def get_location_by_name(name: str) -> Location | None:
    gmaps = googlemaps.Client(key=api.get_google_api_key())
    query_result = gmaps.places(
        query=name
    )

    if len(query_result['results']) < 1:
        return None
    return from_query_result(query_result['results'][0])


def get_nearby_places(page_token: str=None, location: Position=TEST_LOCATION, radius: int=50000, types: any=None, exclude_types: any=[]) -> list[Location]:
    if types is None: types = PLACE_TYPES
    if exclude_types is None: exclude_types = EXCLUDE_PLACE_TYPES
    
    gmaps = googlemaps.Client(key=api.get_google_api_key())

    try:
        query_result: dict = gmaps.places_nearby(
            location=location,
            radius=radius,
            type=", ".join(types),
            page_token=page_token,
        )

        result: list[Location] = []
        for place in query_result['results']:
            parsed_place = from_query_result(place)
            should_append = True
            for type_name in parsed_place.types:
                if type_name in exclude_types:
                    should_append = False
                    break
            if parsed_place.rating < 4 or parsed_place.num_ratings < 100:
                continue # should_append = False
            if should_append:
                result.append(parsed_place)
        
        return result
    
    except googlemaps.exceptions.ApiError as e:
        # print(page_token, location, radius, types)
        # try the same query in case page_token is just bad?
        # print("API Error!")
        raise e


def get_place_reviews(detour: Location) -> Location:
    gmaps = googlemaps.Client(key=api.get_google_api_key())
    
    query_result: dict = gmaps.place(
        place_id=detour.place_id,
        fields=["reviews", "editorial_summary"]
    )

    detour_result = query_result['result']
    if 'editorial_summary' in detour_result.keys():
        detour.information.append(detour_result['editorial_summary']['overview'])
    if 'reviews' in detour_result.keys():
        detour_reviews = detour_result['reviews']
        for detour_review in detour_reviews:
            if detour_review['text']: detour.information.append(detour_review['text'])
    
    return detour if detour.information else None

if __name__ == '__main__':
    # print(str(get_location_by_name("Carson Beach")))
    # print(f'api key is {api.get_api_key()}')
    # token = 'AfLeUgMwiC8X7JO0-thBk8ro369wy9duoKJ5oD-m3ScepBXURtg0npW5QRbYi45fqXvLnORQSbwiz1W1ghkRhy89ibrSS17akDzlrsPDq3L9kXgw62PhJ2UFDy8rSwNQ_YT6xQFMcgt03ujcm-hEGlh3lcuFL_KZ2gdmZ0RAYeHs9SUST40PQoP6ide7cAvtqT1AwwyX_jb0nAOrYyDNOk1gP2JW1qQ8GjuDT0CRDbGTUf6I99B41utdfmLVNjeUmUHf_uAlj4s7NhRDLycReE-pwOywsp4M0zlHNbtkqKAlFFRavGdxBkESHRS1EABdQpXRMVW99r0U3TL_uBJ8IkEHTYm8idk0T4rOec24BcAuJBpgIkWeTvU-UCEXCz1ItQ-mWZ_e7ORiZIuHCYuPteegn0gvUabwB2pFnyTB-sqNMnjetyPQq0BZmxfG08Q33eIYRjh4K2g0GGtBJ12qTSr9YeZvFh9YxFEmCwhNXNA4I2tW3a8yZ3pWqB0VV_XGCVCYO4ppLlg6qt8GXyTaMS1iyS8I1XQ8FmaLYgFDqe80PaqIROub5X0i5YswdssHANfqOG5Ri1Xqw3DJMg6ic5ytHBnmrquEisVYaysvrUdSkp7LK2tM6cFgwysnftt9jrBKVjIF8qUIgNPQJrUozE_T5nDiHzjXJxS0FeXmEi4SIq4RnZem_vpZP917te78eHWBG4yKj1zqariucle36RpxHFX9nMgKT8oYObDvvfXsWXYpt2AL70odqZY5QdecseKTUTc_FWhy-f8033LnTxK2c2cY571fKuEZgn2ab5hYTTgi62aYzLFYdZPCx-JQMPv8jKTswd330rdgaqNkWMrPTWhnZieTD_y6KcEnIHEjdWmkUxkQombDyPb-JhTvnANfpHSHr_kL-16Y9PjqDF872yWtBaP3rPEPt1W67-LCJdLGaME8i7I'
    # for place in get_nearby_places(page_token=token, types=PLACE_TYPES, radius=1000):
    #     pprint(str(place), width=1000)

    for place_index, place in enumerate(get_nearby_places(page_token="",types=PLACE_TYPES,radius=5000)):
        print(place_index)
        pprint(str(place), width=1000)
        pprint(place.get_gmaps_link())
