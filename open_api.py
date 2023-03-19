import api
# See https://platform.openai.com/docs/libraries/python-library
# https://platform.openai.com/docs/api-reference/chat/create
# Also https://pypi.org/project/openai/
import openai
from textwrap import dedent
# https://regexr.com/
import re

from typing import TypeVar, Iterable, NamedTuple

openai.api_key = api.get_openapi_api_key()

MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 100


def send_prompts(prompts: Iterable[str] = None, log=False) -> list[str]:
    """
    Sends a series of prompts to ChatGPT and receives responses.

    :param prompts: the series of prompts.
    :param log: print the response.
    :return: a list of ChatGPT's responses corresponding to each prompt.
    """
    if prompts is None:
        prompts = ["Hello!"]
    response = openai.ChatCompletion.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt} for prompt in prompts
        ],
    )
    if log:
        print(f"Received raw response: {response}")
    return [choice["message"]["content"] for choice in response.choices]


Place = TypeVar("Place")


class TopPlaceQuery(NamedTuple):
    desired_quality: str
    places: dict[Place, str]


def get_top_places(queries: Iterable[TopPlaceQuery], log=False) -> list[Place | None]:
    """
    Given a sequence of queries, where each query consists of
        a desired quality and a mapping of places to descriptions,
    ask ChatGPT to choose the best place for the quality, for each query.
    Each query results in a place or None if the prompt to ChatGPT fails or is in an unrecognizable format.

    :param queries: the list of queries.
    :param log: print the prompts and responses for debugging.
    :return: the place that best matches the desired quality, for each query.
    """
    # prompt engineering
    prologue = dedent("""
        I'll give you a desired quality and a list of descriptions. 
        Select the description that is the best example of the desired quality. 
        Respond with the number of the description, such as [1].
        
        Here is one example:
        The desired quality is rustic.
        [1]: A high school classroom within a bustling city.
        [2]: A modern bedroom within a suburb.
        [3]: A quaint barn house in Iowa.
        [4]: A coral atoll in the middle of the Pacific Ocean.
        The answer is [3].
    """)

    prompts = [prologue]
    places_to_choices = []
    for query in queries:
        desired_quality = query.desired_quality
        places = query.places
        quality_desc = dedent(f"""
            The desired quality is {desired_quality}.
        """)
        choices = ""
        place_to_choice = {}

        for i, (place, description) in enumerate(places.items()):
            identifier = f"[{i + 1}]"
            place_to_choice[identifier] = place
            choices += f"{identifier}: {description}\n"

        epilogue = "The answer is "

        prompt = quality_desc + choices + epilogue

        if log:
            print(f"Created prompt:\n{prompt}")
        prompts.append(prompt)
        places_to_choices.append(place_to_choice)

    responses = send_prompts(prompts, log=log)

    results = []
    for i, response in enumerate(responses):
        if i == 0:
            # first prompt is just to prep ChatGPT
            if log:
                print(f"Received response for opening prompt: {response}")
            continue
        if log:
            print(f"Received response: {response}")

        place_to_choice = places_to_choices[i]
        # try to parse the response
        # Regex for `[3].`, `[92130].`, etc.
        matches = re.findall("\[[0-9]+\]\.", response)
        query_result = None
        if len(matches) > 0:
            try:
                query_result = place_to_choice[matches[0][:-1]]  # trim off period '.'
            except KeyError:
                if log:
                    print(f"Response {response} did not match input choices!")

        # Regex for `[3]`, `[92130]`, etc.
        matches = re.findall("\[[0-9]+\]", response)
        if len(matches) > 0:
            try:
                query_result = place_to_choice[matches[0]]
            except KeyError:
                if log:
                    print(f"Response {response} did not match input choices!")

        print(f"Response {response} did not match known formats!")
        results.append(query_result)

    return results


if __name__ == '__main__':
    print(send_prompts(["Give me an example of a 'warm' location.", "Can you repeat what you just said?"], log=True))
    query1 = TopPlaceQuery(
        desired_quality="warm",
        places={
            "NYC":
                "The largest city in the United States.",
            "Central Park":
                "Central Park is an urban park in New York City. It is the fifth-largest park in the city.",
            "Los Angeles Library":
                "The Los Angeles Public Library provides free and easy access to information, ideas, books and technology that enrich, educate and empower every individual in our city's diverse communities."
        }
    )
    # print(get_top_places([query1], log=True))
