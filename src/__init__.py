import json
import math
from typing import List
from dataclasses import dataclass, asdict
import data_collection
import ml
from data_collection import Location


@dataclass
class DetourInfo:
    place_id: str
    name: str
    total_score: float
    ml_score: float


@dataclass
class DetourQueryResult:
    results: List[DetourInfo]
    additional_results: List[DetourInfo]

    def to_dict(self):
        return asdict(self)


def get_detours(
        keyword: str,
        origin: str,
        destination: str,
        maybe_target_count: int | None = None,
        maybe_model_weight: float | None = None,
        maybe_distance_weight: float | None = None,
        maybe_popularity_weight: float | None = None,
) -> DetourQueryResult:
    """
    Query for suggested detours.

    :return: See `DetourQueryResult`
    """
    # default values
    target_count = maybe_target_count if maybe_target_count else 3
    model_weight = maybe_model_weight if maybe_model_weight else 0.6
    distance_weight = maybe_distance_weight if maybe_distance_weight else 0.3
    popularity_weight = maybe_popularity_weight if maybe_popularity_weight else 0.1

    # get all possible detours
    possible_detours = data_collection.get_locations(origin, destination)

    # get the model evaluation
    def detour_to_info_string(detour: Location) -> str:
        return " ".join(detour.information)

    ml_scores = ml.get_score(keyword,
                             {detour: detour_to_info_string(detour) for detour in possible_detours})

    # filter only the most relevant
    FILTER_THRESHOLD = 0.55  # kinda arbitrary
    filtered_detours = filter(lambda detour: ml_scores[detour] >= FILTER_THRESHOLD,
                              possible_detours)

    # calculate the total score
    total_weight = model_weight + distance_weight + popularity_weight

    def get_popularity_score(detour: Location) -> float:
        normalized_rating = (detour.rating - 1.0) / 4.0
        normalized_num_ratings = 1 - math.exp(-0.01 * detour.num_ratings)
        return 0.5 * normalized_rating + 0.5 * normalized_num_ratings

    def get_total_score(detour: Location) -> float:
        # TODO: Distance calculation
        return (
                model_weight * ml_scores[detour] +
                distance_weight * 1 +
                popularity_weight * get_popularity_score(detour)
        ) / total_weight

    def to_detour_info(detour: Location) -> DetourInfo:
        return DetourInfo(
            place_id=detour.place_id,
            name=detour.name,
            total_score=get_total_score(detour),
            ml_score=ml_scores[detour]
        )

    detours_info = map(to_detour_info, filtered_detours)
    detours_info = list(sorted(detours_info, key=lambda info: info.total_score, reverse=True))

    return DetourQueryResult(
        results=detours_info[:target_count],
        additional_results=detours_info[target_count:],
    )


if __name__ == '__main__':
    # for testing only
    # from pprint import pprint

    TEST_ORIGIN = 'ChIJh2oa9apw44kRPCAIs6WO4NA'  # MIT
    TEST_DESTINATION = 'ChIJLw8wo4Vw44kRWkWR0c03LH4'  # Boston City Hall
    print(json.dumps(get_detours(keyword="natural", origin=TEST_ORIGIN, destination=TEST_DESTINATION).to_dict()))
