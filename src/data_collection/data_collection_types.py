import urllib.parse
from dataclasses import dataclass

from typing import Tuple, List

Position = Tuple[float, float]  # [lat, long]

@dataclass
class Location:
    def __init__(self, name: str, position: Position, place_id: str, types: List[str], rating: float, num_ratings: int):
        self.position = position
        self.name = name
        self.place_id = place_id
        self.types = types
        self.rating = rating
        self.num_ratings = num_ratings
        self.information = []
        self.distance_from_route = None

    def get_gmaps_link(self) -> str:
        return f'https://www.google.com/maps/search/?api=1' \
               f'&query={urllib.parse.quote(self.name)}' \
               f'&query_place_id={urllib.parse.quote(self.place_id)}'

    def __hash__(self):
        return hash(self.place_id)

    def __str__(self):
        return f'{self.name}, ID: {self.place_id}, types: {", ".join(self.types)}'
