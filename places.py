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


def get_location_by_name(name: str) -> Location | None:
    gmaps = googlemaps.Client(key=api.get_api_key())
    query_result = gmaps.places(
        query=name
    )
    # pprint(query_result['results'][0])
    if len(query_result['results']) < 1:
        return None
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
        try:
            pprint(query_result['next_page_token'])
        except KeyError:
            pass

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
    print(str(get_location_by_name("Carson Beach")))
    # print(f'api key is {api.get_api_key()}')
    token = 'AfLeUgOeQfHjlodGXK9MM4kmrAMPZMWZ2ENrhyikFUPmNB4OaBlo9uYFyuA2JycLL0raNhAnX2iaDXdHgWs9Zucgd2-btor1mTzx5Rf1VN_7zNU-h01A8f7FKHXKGzv9HJZSjVm9kmGn_YWTHGsZY87lq4-lYid4_CFYtwlLupkW2-yE3FtS3StnlG45fyFa4SA4_iIMDmmlvHJTSFbZqN_Hf1paRyFPuxjA8dKpAHpe3CD6pLdmlID-MqBATLKF0IGAzWQ-bR61zafukXOShne-0Asd-K7Fs250iSpPoF5oMTBeKGwdjy83Hi1x0k45R4g5q_fFq6oNjO3XFVDSc6m1AtnSqs3vm4aaZYz5zoW0zACgmf8RtSmwqEmlbk-BCTICRd6GwaV_kjve16iBf4jlVC8HnmzhC7Im6N-hmB0W1eX940dxvdh77iAE2sXqzgo65xEaG1uAmLo2hs75io9euWkjsXBfmN9lDbZ8FqOYblSJRpltfNn7yfpWuk1F1-L_78TVMK7eJVr2bzkzKy-ZKEitBePo8DdaBG9FhDenzjFVXVHK5JpM_LjqGOmFF2nUOTzdvS2g3JWV3_gJggn8jfvIUyd3Yg4Xc9mPV0qbXYAhCNR5fdgbO9rsqrxof8m9HpwpnVqUZebUdUPPS_kqA6ftA1p_VLtI3myR7V5tI10Ckt4OboNGJaM4n0PmFZO4r1XJ4m3_SWjk0Hg8lkJ6wGenZMnWqn-XsiB3VE6lqbnpA8Zi-hl_rhWkNbpc5BFhTaDxiFza0qpNx_kdSVFvBE2PR8JVSwu88c2vvXC1Pmr7YQwPui2D_vKDd1BMxl5oixRa6JmCVTNVbgOGP4pDfHUAvwQWnC7MHcqNgdcoILbUB-ByPehtRdtCSh9nO8LbwWC0s1W5Jp1J_9HZewZvu-FjklGbnVoGtXuQm21WOBEhU5HWIaE'

    # for place in get_nearby_places(page_token=token,types=["tourist_attraction"],radius=1000):
    #     pprint(str(place), width=1000)
    #     pprint(place.get_gmaps_link())
