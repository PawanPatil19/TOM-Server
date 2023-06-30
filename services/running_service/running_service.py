import random
from enum import Enum
from modules.maps.maps_util import calculate_distance

import modules.utilities.time as time_utility
from modules.dataformat.data_types import DataTypes
from services.running_service.running_current_data import CurrentData
from . import running_data_handler as running_data_handler


class RunningTrainingMode(Enum):
    SpeedTraining = 0
    DistanceTraining = 1


class SpeedTrainingStats:
    distance_interval = 400  # meters
    time_info_active = 5  # secs
    training_speed_tolerance = 0.5  # min/km


def get_exercise_data(real_wearos):
    total_sec = (time_utility.get_current_millis() - CurrentData.start_time) / 1000
    total_min = (total_sec / 60)

    # receive data from Unity or WearOS client
    socket_data = running_data_handler.get_socket_data()

    # mock service
    if not real_wearos:
        running_data_handler.save_mock_running_data(total_min)

    # skip if no data
    if socket_data is None:
        time_utility.sleep_seconds(0.5)
        return

    # decode data
    socket_data_type, decoded_data = running_data_handler.get_decoded_socket_data(socket_data)
    if socket_data_type is None:
        return

    if socket_data_type == DataTypes.EXERCISE_WEAR_OS_DATA:
        running_data_handler.save_real_running_data(decoded_data)

    elif socket_data_type == DataTypes.REQUEST_RUNNING_DATA:
        running_data_handler.send_running_data(CurrentData.curr_distance, CurrentData.curr_heart_rate,
                                               CurrentData.avg_speed, total_sec)

    elif socket_data_type == DataTypes.REQUEST_DIRECTION_DATA:
        running_data_handler.send_direction_data(CurrentData.start_time, CurrentData.curr_lat, CurrentData.curr_lng,
                                                 CurrentData.dest_lat, CurrentData.dest_lng, CurrentData.bearing)

    elif socket_data_type == DataTypes.REQUEST_SUMMARY_DATA:
        image = running_data_handler.get_static_maps_image(CurrentData.coords, CurrentData.map_size)
        running_data_handler.send_summary_data(CurrentData.exercise_type, CurrentData.start_place,
                                               CurrentData.start_time_string, CurrentData.curr_distance,
                                               CurrentData.avg_speed,
                                               total_sec, image)

    elif socket_data_type == DataTypes.REQUEST_RUNNING_DATA_UNIT:
        running_data_handler.send_running_unit("km", "bpm", "min/km")

    elif socket_data_type == DataTypes.REQUEST_SUMMARY_DATA_UNIT:
        running_data_handler.send_summary_unit(speed="min/km", distance="km")

    elif socket_data_type == DataTypes.REQUEST_TYPE_POSITION_MAPPING:
        running_data_handler.send_type_position_mapping()

    else:
        print(f'Unsupported data type: {socket_data_type}')


def start_training(training_mode, training_route, training_speed=None, real_wearos=False):
    if training_mode == RunningTrainingMode.SpeedTraining:
        start_speed_training(training_route, training_speed, real_wearos)
    elif training_mode == RunningTrainingMode.DistanceTraining:
        start_distance_training(training_route)
    else:
        print('Unsupported training mode')


# assume training route is given as a list of coordinates
def start_speed_training(training_route, training_speed, real_wearos):
    # FIXME: Implement this
    # decide the route
    # show all running info intermittently (say evey 400m for 5 seconds - customizable parameters)
    # show the running speed intermittently when it's higher/lower than the target speed (+ error) - const, may be give visual instructions also
    pass


def start_distance_training(training_route):
    # FIXME: Implement this
    pass
