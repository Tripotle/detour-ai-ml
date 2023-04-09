import asyncio
import pprint
import random
import datetime

import pandas as pd
import plotly.express as px
from nicegui import ui
from nicegui.element import Element
from pprint import pprint

import open_api
from directions import *
from places import Location, get_location_by_name
from model import Model
from open_api import *

px.set_mapbox_access_token(api.get_mapbox_api_key())
model = Model()

origin_name: str = "MIT"
origin: Location | None = None
dest_name: str = "Boston"
dest: Location | None = None
interval = 30
keyword = ""
detours = None

def header(text: str):
    ui.label(text).style(add="font-weight: bold;")
def section(text: str):
    return ui.expansion(text, value=True).classes('w-full bg-slate-200 p-2')
def hline():
    ui.element(tag="div").style(add="""
        height: 1px;
        width: 100%;
        background-color: gray;
    """)
def is_names_valid() -> bool:
    return len(origin_name) > 0 and len(dest_name) > 0
def set_origin_name(e):
    global origin_name
    origin_name = e.value
def set_dest_name(e):
    global dest_name
    dest_name = e.value
def set_keyword(e):
    global keyword
    keyword = e.value
def set_interval(e):
    global interval
    interval = int(e.value)
def set_detours(to: list[Location]):
    global detours
    detours = to
async def submit_route():
    global detours
    if not is_names_valid():
        ui.notify(message=f"Nonempty origin and destination name required")
        return
    update_place_info(origin_info, origin_name)
    update_place_info(dest_info, dest_name)
    waypoints, distance = get_waypoints(origin_name, dest_name)
    update_route_info(waypoints, distance)
    await asyncio.sleep(0.1)  # get the ui to update asyncly. this is stupid, but it works for some reason
    print(f"getting detours at {datetime.datetime.now()}")
    detours_without_reviews = get_detours(origin_name, dest_name, increment=interval)
    detours_with_reviews = get_reviews(detours_without_reviews)
    detours = detours_with_reviews
    update_detours_info(detours_with_reviews)

def update_place_info(container: Element, name: str):
    container.clear()
    try:
        loc = get_location_by_name(name)
        with container:
            ui.label(f"Actual Name: {str(loc.name)}")
            ui.label(f"GMaps ID: {str(loc.place_id)}")
            ui.label(f"(Lat, Lon): {str(loc.position)}")
            ui.label(f"Types: {str(loc.types)}")
            ui.link("Google Maps", target=loc.get_gmaps_link())
    except googlemaps.exceptions.ApiError:
        container.clear()
        with container:
            ui.label(f"Error retrieving location.")
    ui.update(container)
def update_route_info(waypoints: list[tuple[float, float]], distance: float):
    route_info.clear()
    df = pd.DataFrame(waypoints, columns=["lat", "lon"])
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=6)
    with route_info:
        ui.label(f"Distance (in meters): {distance}")
        ui.label(f"Total Waypoints: {len(waypoints)}")
        ui.plotly(fig).classes('w-full h-200')

def update_detours_info(detours: list[Location]):
    global random_detour_info
    detour_info.clear()
    with detour_info:
        ui.label(f"Total locations: {len(detours)}")
        ui.button("Random Location", on_click=lambda: update_random_detour_info(detours))
        random_detour_info = ui.column()
        update_random_detour_info(detours)

    # print(f"got data at {datetime.datetime.now()}")
    df = pd.DataFrame(map(lambda x: (x.name, *x.position), detours), columns=["name", "lat", "lon"])
    # print(f"generated pandas dataframe at {datetime.datetime.now()}")
    fig = px.scatter_mapbox(df, lat="lat", lon="lon", zoom=6)
    # print(f"created px mapbox at {datetime.datetime.now()}")
    with detour_info:
        ui.plotly(fig).classes('w-full h-200')
        # print(f"plotted mapbox at {datetime.datetime.now()}")
def update_random_detour_info(detours: list[Location]):
    random_index = random.randint(0, len(detours)- 1)
    random_detour = detours[random_index]
    random_detour_info.clear()
    with random_detour_info:
        header("Random Selection:")
        ui.label(f"Name: {random_detour.name}")
        ui.label(f"(Lat, Lon): {str(random_detour.position)}")
        formatted_information = '\n'.join(f'\n({i}): {info[:200]}' for i, info in enumerate(random_detour.information))
        ui.label(f"Sample Review(s): {formatted_information}").style("white-space: pre-line;")
        ui.link("Google Maps", target=random_detour.get_gmaps_link())

def run_doc2vec_model():
    top_locations = model.top(keyword, detours)
    results_info.clear()
    with results_info:
        with ui.row():
            with ui.column():
                header("Best Locations")
                for i, (loc, sim) in enumerate(reversed(top_locations[-len(top_locations)//2:])):
                    ui.label(f"Rank: {i}")
                    ui.label(f"Name: {loc.name}")
                    ui.label(f"Similarity: {sim}")
                    ui.link("Google Maps", target=loc.get_gmaps_link())
            with ui.column():
                header("Worst Locations")
                for i, (loc, sim) in enumerate(top_locations[:len(top_locations)//2]):
                    ui.label(f"Rank: {i}")
                    ui.label(f"Name: {loc.name}")
                    ui.label(f"Similarity: {sim}")
                    ui.link("Google Maps", target=loc.get_gmaps_link())

def run_chatgpt():
    query = TopPlaceQuery(
        desired_quality=keyword,
        places={loc: (loc.name + ' '.join(loc.information))[:80] for loc in detours},
    )
    top_locations = open_api.rank_places(query)
    results_info.clear()
    with results_info:
        with ui.row():
            with ui.column():
                header("Best Locations")
                for i, loc in enumerate(reversed(top_locations[:len(top_locations)//2])):
                    ui.label(f"Rank: {i}")
                    ui.label(f"Name: {loc.name}")
                    ui.link("Google Maps", target=loc.get_gmaps_link())
            with ui.column():
                header("Worst Locations")
                for i, loc in enumerate(top_locations[-len(top_locations)//2:]):
                    ui.label(f"Rank: {i}")
                    ui.label(f"Name: {loc.name}")
                    ui.link("Google Maps", target=loc.get_gmaps_link())

ui.label("DetourAI ML Backend Demo")\
    .style(add="font-size: 2em;")
with ui.row().style(add="display: flex; flex-direction: row; align-items: start; width: 100%; justify-content: space-between;"):
    with ui.column():
        ui.input(label="Origin",
                 on_change=set_origin_name,
                 value=origin_name
                 )
        origin_info = section("GMaps Data")
    with ui.column():
        ui.input(label="Destination", on_change=set_dest_name, value=dest_name)
        dest_info = section("GMaps Data")
    ui.number(label="Waypoint Interval",
              value=interval,
              on_change=set_interval,
              validation={'Positive integer': lambda value: int(value) > 0}
              )
    ui.button("Go", on_click=submit_route)

hline()
route_info = section("Route Data")
hline()
detour_info = section("Detours Data")
random_detour_info = None
hline()
ui.input(label="Keyword", on_change=set_keyword)
ui.button("Run Doc2Vec Algorithm", on_click=run_doc2vec_model)
ui.button("Ask ChatGPT (Note: inputs may be trimmed for length)", on_click=run_chatgpt)
results_info = section("Results")
ui.run()
