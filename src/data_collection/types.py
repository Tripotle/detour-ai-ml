import urllib.parse


Position = tuple[float, float]  # [lat, long]


class Location:
    def __init__(self, name: str, position: Position, place_id: str, types: list[str], rating: int, num_ratings: int):
        self.position = position
        self.name = name
        self.place_id = place_id
        self.types = types
        self.rating = rating
        self.num_ratings = num_ratings
        self.information = []

    def get_gmaps_link(self) -> str:
        return f'https://www.google.com/maps/search/?api=1' \
               f'&query={urllib.parse.quote(self.name)}' \
               f'&query_place_id={urllib.parse.quote(self.place_id)}'

    def __str__(self):
        return f'{self.name}, ID: {self.place_id}, types: {", ".join(self.types)}'
