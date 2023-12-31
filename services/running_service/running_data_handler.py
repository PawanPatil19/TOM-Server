import asyncio
import logging
import math
import random

from google.protobuf.message import DecodeError

from modules.maps.direction_data import DirectionData
from modules.maps.maps_util import calculate_distance, get_direction_str

import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server
from config import STATIC_MAPS_OPTION
from modules.dataformat import direction_data_pb2
from modules.dataformat import exercise_wear_os_data_pb2
from modules.dataformat import request_data_pb2
from modules.dataformat import running_data_pb2
from modules.dataformat import socket_data_pb2
from modules.dataformat import summary_data_pb2
from modules.dataformat import type_position_mapping_data_pb2
from modules.dataformat.data_types import DataTypes
from modules.maps.maps import get_static_maps, get_walking_directions
from services.running_service.running_current_data import CurrentData
from services.running_service.running_display import RunningDataDisplayPosition


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()


##############################################################################################################
############################################## Parsing data ##################################################
##############################################################################################################
def get_decoded_socket_data(socket_data):
    if socket_data is None or isinstance(socket_data, str):
        logging.error('Received data is not a valid socket_data instance')
        return None, None

    try:
        socket_data_msg = socket_data_pb2.SocketData()
        socket_data_msg.ParseFromString(socket_data)

        data_type = socket_data_msg.data_type
        data = socket_data_msg.data

        if data_type == DataTypes.EXERCISE_WEAR_OS_DATA:
            return decode_exercise_wear_os_data(data)
        elif is_request_data_type(data_type):
            return decode_request_data(data_type, data)
        else:
            logging.error('Unknown socket_data protobuf type')
            return data_type, None
    except DecodeError:
        logging.error('Received data is not a valid socket_data protobuf message')
        return None, None


def decode_exercise_wear_os_data(data):
    try:
        exercise_wear_os_data = exercise_wear_os_data_pb2.ExerciseWearOsData()
        exercise_wear_os_data.ParseFromString(data)

        return DataTypes.EXERCISE_WEAR_OS_DATA, exercise_wear_os_data
    except DecodeError:
        logging.error('Received data is not a valid exercise_wear_os_data protobuf message')
        return None, None


def decode_request_data(request_type, data):
    try:
        request_data = request_data_pb2.RequestData()
        request_data.ParseFromString(data)

        return request_type, request_data
    except DecodeError:
        logging.error(
            'Received data is not a valid request_data protobuf message')
        return None, None


##############################################################################################################
############################################## Saving data ###################################################
##############################################################################################################


def save_mock_running_data(total_min):
    CurrentData.curr_distance += (random.randint(1, 3) / 1000)  # in km
    CurrentData.curr_heart_rate = random.randint(70, 80)
    CurrentData.avg_speed = total_min / CurrentData.curr_distance


def save_mock_coords(training_route):
    CurrentData.coords = training_route


def save_real_running_data(decoded_data):
    CurrentData.start_time = decoded_data.start_time
    CurrentData.avg_speed = -1.0
    if decoded_data.speed_avg > 0:
        CurrentData.avg_speed = 1000 / (60 * decoded_data.speed_avg)  # min/km
    CurrentData.curr_distance = decoded_data.distance / 1000  # km
    CurrentData.curr_heart_rate = decoded_data.heart_rate
    CurrentData.exercise_type = decoded_data.exercise_type
    CurrentData.curr_lat = decoded_data.curr_lat
    CurrentData.curr_lng = decoded_data.curr_lng
    # CurrentData.dest_lat = decoded_data.dest_lat
    # CurrentData.dest_lng = decoded_data.dest_lng
    CurrentData.bearing = decoded_data.bearing
    save_real_coords()


def save_real_coords():
    # set a min distance between prev coordinate and current coordinate, in meters
    # this is to prevent adding points that are too close to each other
    threshold_distance = 30
    if len(CurrentData.coords) > 0:
        prev_lat, prev_lng = CurrentData.coords[-1]

        distance = calculate_distance(prev_lat, prev_lng, CurrentData.curr_lat, CurrentData.curr_lng)
        if distance >= threshold_distance:
            CurrentData.coords.append((CurrentData.curr_lat, CurrentData.curr_lng))
    else:
        CurrentData.coords.append((CurrentData.curr_lat, CurrentData.curr_lng))


##############################################################################################################
############################################## Sending data ##################################################
##############################################################################################################


def send_running_data(distance=None, heart_rate=None, speed=None, duration=None, include_time=None):
    running_data_proto = running_data_pb2.RunningData()

    if distance is not None:
        running_data_proto.distance = f'{distance:.2f}'

    if heart_rate is not None:
        running_data_proto.heart_rate = f'{int(heart_rate)}'

    if speed is not None:
        if speed == -1.0:
            running_data_proto.speed = 'N/A'
        else:
            running_data_proto.speed = f'{speed:.2f}'

    if duration is not None:
        running_data_proto.duration = time_utility.get_hh_mm_ss_format(int(duration))

    if include_time is True:
        running_data_proto.time = time_utility.get_date_string("%I:%M %p")

    running_data_bytes = wrap_message_with_metadata(running_data_proto, DataTypes.RUNNING_DATA)
    send_socket_server(running_data_bytes)


def send_running_unit(distance='', heart_rate='', speed='', duration='', time=''):
    running_unit_data_proto = running_data_pb2.RunningData(
        distance=distance,
        heart_rate=heart_rate,
        speed=speed,
        duration=duration,
        time=time,
    )
    running_unit_bytes = wrap_message_with_metadata(running_unit_data_proto, DataTypes.RUNNING_UNIT)
    send_socket_server(running_unit_bytes)


def send_running_alert(speed=None, distance=None, instruction=None):
    running_alert_data_proto = running_data_pb2.RunningData(
        speed=speed,
        distance=distance,
        instruction=instruction,
    )
    running_alert_bytes = wrap_message_with_metadata(running_alert_data_proto, DataTypes.RUNNING_ALERT)
    send_socket_server(running_alert_bytes)


# change this args
def send_direction_data(dest_dist_str=None, dest_duration_str=None, curr_dist_str=None, curr_duration_str=None,
                        curr_instr=None, curr_direction=None, num_steps=None):
    direction_data_proto = direction_data_pb2.DirectionData()
    if dest_dist_str is not None:
        direction_data_proto.dest_dist = dest_dist_str

    if dest_duration_str is not None:
        direction_data_proto.dest_duration = dest_duration_str

    if curr_dist_str is not None:
        direction_data_proto.curr_dist = curr_dist_str

    if curr_duration_str is not None:
        direction_data_proto.curr_duration = curr_duration_str

    if curr_instr is not None:
        direction_data_proto.curr_instr = curr_instr

    if curr_direction is not None:
        direction_data_proto.curr_direction = str(curr_direction)

    if num_steps is not None:
        direction_data_proto.num_steps = num_steps

    direction_data_bytes = wrap_message_with_metadata(direction_data_proto, DataTypes.DIRECTION_DATA)
    send_socket_server(direction_data_bytes)


def send_summary_data(exercise_type, start_place, start_time_string, distance, speed, duration, image):
    summary_data_proto = summary_data_pb2.SummaryData(
        detail=f'{exercise_type} at {start_place} on {start_time_string}',
        distance=f'{distance:.2f}',
        speed=f'{speed:.2f}',
        duration=time_utility.get_hh_mm_ss_format(int(duration)),
        image=image
    )
    summary_data_bytes = wrap_message_with_metadata(summary_data_proto, DataTypes.SUMMARY_DATA)
    send_socket_server(summary_data_bytes)


def send_summary_unit(detail='', distance='', speed='', duration=''):
    summary_unit_data_proto = summary_data_pb2.SummaryData(
        detail=detail,
        distance=distance,
        speed=speed,
        duration=duration,
    )
    summary_unit_bytes = wrap_message_with_metadata(
        summary_unit_data_proto, DataTypes.SUMMARY_UNIT)
    send_socket_server(summary_unit_bytes)


def send_type_position_mapping():
    type_position_mapping_data = type_position_mapping_data_pb2.TypePositionMappingData(
        running_distance_position=RunningDataDisplayPosition.Top.value,
        running_heartrate_position=RunningDataDisplayPosition.TopLeft.value,
        running_speed_position=RunningDataDisplayPosition.TopCenter.value,
        running_duration_position=RunningDataDisplayPosition.TopRight.value,
        running_time_position=RunningDataDisplayPosition.BottomLeft.value,
        summary_detail_position=RunningDataDisplayPosition.Top.value,
        summary_distance_position=RunningDataDisplayPosition.Left.value,
        summary_speed_position=RunningDataDisplayPosition.Center.value,
        summary_duration_position=RunningDataDisplayPosition.Right.value,
    )
    type_mapping_bytes = wrap_message_with_metadata(type_position_mapping_data, DataTypes.TYPE_POSITION_MAPPING_DATA)
    send_socket_server(type_mapping_bytes)


##############################################################################################################
################################################# Utils ######################################################
##############################################################################################################
def is_request_data_type(data_type):
    return data_type in [DataTypes.REQUEST_RUNNING_DATA,
                         DataTypes.REQUEST_SUMMARY_DATA,
                         DataTypes.REQUEST_DIRECTION_DATA,
                         DataTypes.REQUEST_RUNNING_DATA_UNIT,
                         DataTypes.REQUEST_SUMMARY_DATA_UNIT,
                         DataTypes.REQUEST_TYPE_POSITION_MAPPING,
                         ]


def wrap_message_with_metadata(data, data_type):
    socket_data = socket_data_pb2.SocketData(
        data_type=data_type,
        data=data.SerializeToString()
    )

    return socket_data.SerializeToString()


def get_directions_real(start_time, training_route, bearing, option, ors_option=0):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_walking_directions(start_time, training_route, bearing, option, ors_option))
    loop.close()
    return result


def get_directions_mock():
    dest_dist = random.randint(500, 1500)
    dest_dist_str = f'{dest_dist} m'
    dest_duration = random.randint(120, 360)
    dest_duration_str = f"{math.ceil(dest_duration / 60)} min"

    instruction_map = {
        "straight": "Head north",
        "turn_slight_right": "Head northeast",
        "turn_right": "Head east",
        "turn_sharp_right": "Head southeast",
        "u_turn": "Head south",
        "turn_sharp_left": "Head southwest",
        "turn_left": "Head west",
        "turn_slight_left": "Head northwest"
    }

    waypoint_dist = random.randint(21, 400)
    waypoint_dist_str = f'{waypoint_dist} m'
    waypoint_duration = random.randint(1, 50)
    waypoint_duration_str = f'{math.ceil(waypoint_duration / 60)} min'
    curr_dist = random.randint(21, waypoint_dist)
    curr_dist_str = f'{curr_dist} m'
    curr_duration = random.randint(1, waypoint_duration)
    curr_duration_str = f'{math.ceil(curr_duration) / 60} min'
    num_steps = random.randint(2, 15)
    rand_dir = random.randint(0, 360)
    curr_instr = instruction_map.get(get_direction_str(rand_dir))

    return DirectionData(
        CurrentData.start_time,
        time_utility.get_current_millis(),
        dest_dist,
        dest_dist_str,
        dest_duration,
        dest_duration_str,
        curr_dist,
        curr_dist_str,
        curr_duration,
        curr_duration_str,
        curr_instr,
        rand_dir,
        str(num_steps),
        waypoint_dist,
        waypoint_dist_str,
        waypoint_duration,
        waypoint_duration_str
    )


def get_static_maps_image():
    # get the last known coordinates if not already in the list
    if (CurrentData.curr_lat, CurrentData.curr_lng) not in CurrentData.coords:
        CurrentData.coords.append((CurrentData.curr_lat, CurrentData.curr_lng))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    image_bytes = loop.run_until_complete(
        get_static_maps(CurrentData.coords, CurrentData.map_size, STATIC_MAPS_OPTION))
    loop.close()
    return image_bytes
