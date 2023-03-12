import api
import googlemaps
from pprint import pprint
import urllib.parse

# Kresge
TEST_ADDRESS = '48 Massachusetts Ave w16, Cambridge, MA 02139'
# can get from geocode API
LOCATION = (42.3581083, -71.0948251)

# https://developers.google.com/maps/documentation/places/web-service/supported_types
PLACE_TYPES: list[str] = [
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
    "lodging",
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

EXCLUDE_PLACE_TYPES: list[str] = [
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

Position = tuple[float, float]  # [lat, long]


class Location:

    def __init__(self, name: str, position: Position, place_id: str, types: list[str]):
        self.position = position
        self.name = name
        self.place_id = place_id
        self.types = types

    def get_gmaps_link(self) -> str:
        return f'https://www.google.com/maps/search/?api=1' \
               f'&query={urllib.parse.quote(self.name)}' \
               f'&query_place_id={urllib.parse.quote(self.place_id)}'

    def __str__(self):
        return f'{self.name}, ID: {self.place_id}, types: {", ".join(self.types)}'


def from_query_result(query_result: any) -> Location:
    return Location(name=query_result['name'],
                    position=(query_result['geometry']['location']['lat'], query_result['geometry']['location']['lng']),
                    place_id=query_result['place_id'], types=query_result['types'])


def get_location_by_name(name: str) -> Location:
    gmaps = googlemaps.Client(key=api.get_api_key())
    query_result = gmaps.places(
        query=name
    )
    # pprint(query_result['results'][0])
    return from_query_result(query_result['results'][0])


def get_nearby_places(page_token: str = None, location=LOCATION, radius=200, types=None, exclude_types=None) -> list[Location]:
    if types is None:
        types = PLACE_TYPES
    if exclude_types is None:
        exclude_types = EXCLUDE_PLACE_TYPES
    gmaps = googlemaps.Client(key=api.get_api_key())

    try:
        query_result: dict = gmaps.places_nearby(
            page_token=page_token,
            location=location,
            radius=radius,
            type=", ".join(types),
        )
        pprint(query_result['next_page_token'])

        result: list[Location] = []
        for place in query_result['results']:
            location = from_query_result(place)
            should_append = True
            for type_name in location.types:
                if type_name in exclude_types:
                    should_append = False
                    break
            if should_append:
                result.append(location)

        # if 'next_page_token' in query_result.keys():
        #     result.extend(get_nearby_places(
        #         page_token=query_result['next_page_token'],
        #         location=location,
        #         radius=radius,
        #         types=types,
        #         exclude_types=exclude_types
        #     ))

        return result
    except googlemaps.exceptions.ApiError as e:
        print("API Error!")
        raise e


if __name__ == '__main__':
    # print(str(get_location_by_name("Great Dome")))
    # print(f'api key is {api.get_api_key()}')
    token = 'AfLeUgPTvH9rLlEmJMIhy6lYO_8i-A7ldunk7F8LlBc6kUGYy6XjuRTpA7PqT7qqCU4zxq_5Y_Zoo-iRUD-sRC3F4G385THtojTZxlqHslUPG3RSijo6JQ270qtUA1htxlR4YdtLSjFmWOOMLjMUb0RjSuxZQOEFFczjEhaMp3Z7GMF_aW6rA0-4_iP_mKXjHoyM5wXgiO3Q5g_NmLL9M_H0sbiOk5IfO9gjfWyXHveJUZdjVB4UR_2B7L60zFeE-sp2aUW8appJaueHrYS-A1vb_dzH-03o8HJJaNc_B6Hq3Blt_QKmV0I2rJwPvdud9-JVb4haiV4atomak7sqclRDRmedcNPrnfBPhIZ5uiyu7cPp6Wt0R_GYfJhYYkU7h_iZTuhIUl3i5W5qUy_evNo5OOVxdwtMWFe6AIIPhWnba7PEHq-7vNW7dq8c-dPAG9SmiJjUn0E09k3qtoynpzibaTYIyfUwQDG7faWGQMTEMivx0-yTBt7x0m6xgz1ThDKi1Ycz9mghSZqvc0iQAVCVKOW9KwnP7qP4aokPRLJMlGOfX1Dqw35iKRznMEavsZLNX6gt_IeRN-ZAdm_EnciPEqVm92LkrmUzQn82w05We3hR9CfEeUD0_HNK5hV5Ftd1-hZ10EgZqH8dxBRzkBzpgK3TQdqwvn8kVqToZkbZ7UZ9BaAgqw_DVZJUdGUGADI0IheKKZ5JganLt0keySzmACMCwVvNtd4pYCHivrMxbV0WtVwoepkOpbnRKzGuMwt74E1B8oc9wxX2Xg1P3aW4zTGh9UmRqZ_hIns12v38PoOejoqa-XPYFln0CAF3gcZWWmdd4VpmNv7RVGfFzeoLJGdpeXSY716Z04svXXC26HkX8R9IdausrYkXoVa1f8DGQBalTLCGKDpWYm8xVu1fHl6jL11NmZOYisevx4azJQH1_R_f_ChN_YXXo2MUC6g'

    for place in get_nearby_places(page_token=token,radius=1000):
        pprint(str(place), width=1000)
        pprint(place.get_gmaps_link())
