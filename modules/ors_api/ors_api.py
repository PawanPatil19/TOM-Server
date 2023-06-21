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


async def find_directions_ors(start_time, src_lat, src_lng, dest_lat, dest_lng, bearing, option):
    coords = [[src_lng, src_lat], [dest_lng, dest_lat]]
    client = create_ors_client(option)

    response = client.directions(coords, profile='foot-walking', format="geojson", maneuvers=True)

    features = response["features"]
    properties = features[0]["properties"]
    segments = properties["segments"]
    summary = properties["summary"]
    dest_dist = summary["distance"]
    dest_duration = summary["duration"]
    steps = segments[0]["steps"]
    print("Steps:", steps)

    curr_step = steps[0]
    curr_dist = curr_step["distance"]
    curr_duration = curr_step["duration"]
    curr_instr = curr_step["instruction"]
    curr_maneuver = curr_step["maneuver"]
    # curr_bearing_before = curr_maneuver["bearing_before"]
    curr_bearing_before = bearing
    curr_bearing_after = curr_maneuver["bearing_after"]
    curr_direction = maps_util.get_directions_from_bearings(curr_bearing_before, curr_bearing_after)

    next_direction = None
    if len(steps) > 1:
        next_step = steps[1]
        next_maneuver = next_step["maneuver"]
        next_bearing_before = next_maneuver["bearing_before"]
        next_bearing_after = next_maneuver["bearing_after"]
        next_direction = maps_util.get_directions_from_bearings(next_bearing_before, next_bearing_after)
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
        curr_direction=curr_direction,
        next_direction=next_direction
    )
