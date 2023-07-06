import json
import math
import time

import openrouteservice as openrouteservice

from config import ORS_CREDENTIAL_FILE
from modules.maps import maps_util
from modules.maps.direction_data import DirectionData

KEY_MAP_API = 'map_api_key'


# return {"map_api_key": "YYY"}
def read_ors_credential():
    print('Reading ORS credentials')
    with open(ORS_CREDENTIAL_FILE, 'r') as f:
        credential = json.load(f)
    return credential


def get_ors_credential(key, credential=None):
    _credential = credential
    if _credential is None:
        _credential = read_ors_credential()

    return _credential[key]


def create_ors_client(option):
    if option == 0:
        return openrouteservice.Client(key=get_ors_credential(KEY_MAP_API))
    elif option == 1:
        return openrouteservice.Client(base_url='http://localhost:8080/ors')
    else:
        raise ValueError("Invalid option.")


async def find_directions_ors(start_time, coordinates, bearing, option):
    # lat lng is switched for ors
    switch_coordinates = [[coord[1], coord[0]] for coord in coordinates]

    client = create_ors_client(option)
    response = client.directions(switch_coordinates, profile='foot-walking', format="geojson", maneuvers=True)

    features = response["features"]
    properties = features[0]["properties"]
    segments = properties["segments"]
    summary = properties["summary"]
    dest_dist = summary["distance"]
    dest_duration = summary["duration"]
    waypoint_dist = math.ceil(segments[0]["distance"])
    waypoint_dist_str = f"{waypoint_dist} m"
    waypoint_duration = math.ceil(segments[0]["duration"])
    waypoint_duration_str = f"{math.ceil(waypoint_duration / 60)} min"
    steps = segments[0]["steps"]

    curr_step = steps[0]
    curr_dist = curr_step["distance"]
    curr_duration = curr_step["duration"]
    curr_instr = curr_step["instruction"]
    curr_maneuver = curr_step["maneuver"]
    # curr_bearing_before = curr_maneuver["bearing_before"]
    curr_bearing_before = bearing
    curr_bearing_after = curr_maneuver["bearing_after"]
    curr_direction = maps_util.calculate_turn_angle(curr_bearing_before, curr_bearing_after)

    # last step in each segment is just 0m to indicate waypoint reached, so we use the second last step instead
    num_coordinates = len(coordinates)
    num_steps = 0
    for segment in segments:
        num_steps += len(segment["steps"])
    num_steps -= num_coordinates - 1
    if num_steps <= 0:
        num_steps = 1
    
    return DirectionData(
        start_time=start_time,
        update_time=int(time.time() * 1000),
        dest_dist=math.ceil(dest_dist),
        dest_dist_str=f"{math.ceil(dest_dist)} m",
        dest_duration=math.ceil(dest_duration),
        dest_duration_str=f"{math.ceil(dest_duration / 60)} min",
        curr_dist=math.ceil(curr_dist),
        curr_dist_str=f"{math.ceil(curr_dist)} m",
        curr_duration=math.ceil(curr_duration),
        curr_duration_str=f"{math.ceil(curr_duration / 60)} min",
        curr_instr=curr_instr,
        curr_direction=str(curr_direction),
        num_steps=str(num_steps),
        waypoint_dist=waypoint_dist,
        waypoint_dist_str=waypoint_dist_str,
        waypoint_duration=waypoint_duration,
        waypoint_duration_str=waypoint_duration_str,
    )
