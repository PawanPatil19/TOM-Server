import json
import math
import re
import time
from io import BytesIO

import googlemaps
from PIL import Image
from googlemaps.maps import StaticMapPath, StaticMapMarker

from config import GOOGLE_CREDENTIAL_FILE
from modules.maps.direction_data import DirectionData
from modules.maps.location_data import LocationData
from modules.maps.maps_util import calculate_bearing_after, calculate_turn_angle

KEY_MAP_API = 'map_api_key'


# return {"map_api_key": "YYY"}
def read_google_credential():
    print('Reading Google credentials')
    with open(GOOGLE_CREDENTIAL_FILE, 'r') as f:
        credential = json.load(f)
    return credential


def get_google_credential(key, credential=None):
    _credential = credential
    if _credential is None:
        _credential = read_google_credential()

    return _credential[key]


def get_google_client():
    return googlemaps.Client(key=get_google_credential(KEY_MAP_API))


async def find_locations_google(search_text, location=None):
    client = get_google_client()
    params = {"query": search_text}
    if location is not None:
        params["location"] = location
    response = client.places(**params)

    location_data_list = []
    for result in response["results"]:
        lat_lng = result["geometry"]["location"]
        address = result.get("formatted_address", "")
        name = result["name"]
        lat = lat_lng["lat"]
        lng = lat_lng["lng"]

        location_data = LocationData(address, name, lat, lng)
        location_data_list.append(location_data)

    return location_data_list


async def find_directions_google(start_time, coordinates, bearing):
    src = coordinates[0]
    dest = coordinates[-1]
    waypoints = coordinates[1:-1]

    client = get_google_client()
    directions_result = client.directions(
        origin=src,
        destination=dest,
        waypoints=waypoints,
        mode="walking"
    )

    route = directions_result[0]
    num_steps = 0
    dest_dist = 0
    dest_duration = 0
    for leg in route['legs']:
        num_steps += len(leg['steps'])
        dest_dist += leg['distance']['value']
        dest_duration += leg['duration']['value']
    dest_dist_str = f"{dest_dist} m"
    dest_duration_str = f"{math.ceil(dest_duration / 60)} min"

    curr_leg = route['legs'][0]
    curr_dist = curr_leg['steps'][0]['distance']['value']
    curr_dist_str = curr_leg['steps'][0]['distance']['text']
    curr_duration = curr_leg['steps'][0]['duration']['value']
    curr_duration_str = curr_leg['steps'][0]['duration']['text']
    curr_instr = curr_leg['steps'][0]['html_instructions']
    curr_step_end_lat = curr_leg['steps'][0]['end_location']['lat']
    curr_step_end_lng = curr_leg['steps'][0]['end_location']['lng']
    curr_bearing_after = calculate_bearing_after(src[0], src[1], curr_step_end_lat, curr_step_end_lng)
    curr_direction = calculate_turn_angle(bearing, curr_bearing_after)
    waypoint_dist = curr_leg['distance']['value']
    waypoint_dist_str = curr_leg['distance']['text']
    waypoint_duration = curr_leg['duration']['value']
    waypoint_duration_str = curr_leg['duration']['text']

    return DirectionData(
        start_time=start_time,
        update_time=int(time.time() * 1000),
        dest_dist=dest_dist,
        dest_dist_str=dest_dist_str,
        dest_duration=dest_duration,
        dest_duration_str=dest_duration_str,
        curr_dist=curr_dist,
        curr_dist_str=curr_dist_str,
        curr_duration=curr_duration,
        curr_duration_str=curr_duration_str,
        # regex to remove html tags, from https://stackoverflow.com/a/12982689/18753727
        curr_instr=re.sub(re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});'), '', curr_instr),
        curr_direction=str(curr_direction),
        num_steps=str(num_steps),
        waypoint_dist=waypoint_dist,
        waypoint_dist_str=waypoint_dist_str,
        waypoint_duration=waypoint_duration,
        waypoint_duration_str=waypoint_duration_str
    )


async def find_static_maps_google(coordinates, size):
    client = get_google_client()
    path = StaticMapPath(
        points=coordinates,
        weight=3,
        color="red"
    )

    markers = [StaticMapMarker(locations=coordinates[0], color="blue")]
    if len(coordinates) > 1:
        markers.append(StaticMapMarker(locations=coordinates[-1], color="red"))

    static_map = client.static_map(
        size=size, path=path, format="jpg", markers=markers)
    static_map_bytes = b"".join(static_map)

    # Uncomment to save image in a jpg file
    # image = Image.open(BytesIO(static_map_bytes))
    # image.show()
    # image.save("static_map_1.jpeg", format="JPEG", quality=100)

    return static_map_bytes
