import json
import re
import time

import googlemaps

from modules.maps.direction_data import DirectionData
from modules.maps.location_data import LocationData

GOOGLE_CREDENTIAL_FILE = '../../config/google_credential.json'  # has the 'map_api_key', ...
KEY_MAP_API = 'map_api_key'


# return {"map_api_key": "YYY"}
def read_google_credential(filepath):
    print('Reading Google credentials')
    with open(filepath, 'r') as f:
        credential = json.load(f)
    return credential


def get_google_credential(key, filepath, credential=None):
    _credential = credential
    if _credential is None:
        _credential = read_google_credential(filepath)

    return _credential[key]


client = googlemaps.Client(key=get_google_credential(KEY_MAP_API, GOOGLE_CREDENTIAL_FILE))


async def find_locations_google(search_text):
    response = client.places(query=search_text)

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


async def find_directions_google(start_time, src_lat, src_lng, dest_lat, dest_lng, bearing):
    src = f"{src_lat}, {src_lng}"
    dest = f"{dest_lat}, {dest_lng}"
    directions_result = client.directions(
        origin=src,
        destination=dest,
        mode="walking"
    )

    route = directions_result[0]
    leg = route['legs'][0]
    dest_dist = leg['distance']['value']
    dest_dist_str = leg['distance']['text']
    dest_duration = leg['duration']['value']
    dest_duration_str = leg['duration']['text']
    curr_dist = leg['steps'][0]['distance']['value']
    curr_dist_str = leg['steps'][0]['distance']['text']
    curr_duration = leg['steps'][0]['duration']['value']
    curr_duration_str = leg['steps'][0]['duration']['text']
    curr_instr = leg['steps'][0]['html_instructions']
    curr_direction = leg['steps'][0]['maneuver'] if 'maneuver' in leg['steps'][0] else 'straight'
    next_direction = leg['steps'][1]['maneuver'] if len(leg['steps']) > 1 and 'maneuver' in leg['steps'][1] else None

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
        curr_direction=curr_direction,
        next_direction=next_direction
    )
