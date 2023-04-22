import math
from typing import Dict, TypeVar
import ml.model
import ml.open_api

Location = TypeVar("Location")


def get_score(keyword: str, locations: Dict[Location, str]) -> Dict[Location, float]:
    """
    Given a mapping of locations to some form of string information and a keyword,
    return a mapping of those locations to a score
    based on the similarity of the information and the keyword.

    :param locations: dictionary of (Location -> information)
    :param keyword: the keyword. Must be a single keyword with no spaces, punctuation, etc.
    :return: dictionary of (Location - score) where score in [-1, 1]
    """

    base_model_score: Dict[Location, float] = {}
    base_model = model.Model()
    for (location, info) in locations.items():
        base_model_score[location] = base_model.compute_score(keyword, info)

    sorted_base = sorted(base_model_score.keys(), key=lambda x: base_model_score[x])

    # Estimate number of tokens to avoid reaching OpenApi's 4097 token request limit
    # See this article:
    # https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
    # You can also use this tool to estimate:
    # https://platform.openai.com/tokenizer

    estimated_length = 130  # include initial prompt engineering header with keyword, and prologue
    total_included = 0

    # reverse because we want the highest scores first
    for location in reversed(sorted_base):
        location_information = locations[location]
        # 3 comes from the numbering i.e. [4]:, 1.5 factor is to be generous
        added_length = estimated_length + 3 + math.ceil(1.5 * len(location_information.split()))
        new_total = total_included + 1

        # we must subtract the length of the response
        if added_length > 4097 - 3 * new_total:
            break
        estimated_length = added_length
        total_included = new_total

    open_api_rank = open_api.rank_places(open_api.TopPlaceQuery(
        keyword,
        {
            location: locations[location] for location in sorted_base[-total_included:]
        }
    ))

    # query failed
    if open_api_rank is None:
        return base_model_score

    open_api_indices = {
        location: index for (index, location) in enumerate(open_api_rank)
    }

    def calc_score(loc: Location) -> float:
        open_api_index = open_api_indices.get(loc)
        if open_api_index is None:
            return 0.5 * base_model_score[loc]
        return 0.5 * base_model_score[loc] + 0.5 * (len(open_api_indices) - open_api_index) / len(open_api_indices)

    return {
        location: calc_score(location) for location in locations
    }


if __name__ == '__main__':
    # Strictly for testing purposes
    from pprint import pprint

    test_locations = {
        "NYC":
            "The largest city in the United States.",
        "Central Park":
            "Central Park is an urban park in New York City. It is the fifth-largest park in the city.",
        "Los Angeles Library":
            "The Los Angeles Public Library provides free and easy access to information, ideas, books and "
            "technology that enrich, educate and empower every individual in our city's diverse communities.",
        "Amazon rainforest":
            "The Amazon rainforest is a moist broadleaf tropical rainforest in the Amazon biome that covers most"
            "of the Amazon basin of South America",
        "Arnold Arboretum":
            "The Arnold Arboretum's collection of temperate trees, shrubs, and vines has a particular emphasis on the "
            "plants of the eastern United States and eastern Asia,[3] where arboretum staff and colleagues are "
            "actively sourcing new material on plant collecting expeditions."
    }

    pprint(get_score("natural", test_locations))
