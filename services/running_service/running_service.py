from queue import Queue
from enum import Enum

import modules.utilities.time as time_utility
from modules.dataformat.data_types import DataTypes
from services.running_service.running_current_data import CurrentData
from . import running_data_handler as running_data_handler


class RunningTrainingMode(Enum):
    SpeedTraining = 0
    DistanceTraining = 1


class SpeedTrainingStats:
    distance_interval = 0.4  # km
    time_info_active = 5  # secs
    training_speed_tolerance = 0.5  # min/km
    correct_speed = False


total_sec = 0
request_queue = Queue()
is_processing_running_request = False


def is_item_in_queue(queue, item):
    with queue.mutex:
        return item in queue.queue


def get_exercise_data(real_wearos):
    global total_sec
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
        # check is_processing_running_request just in case the next request is sent before the previous request is
        # processed finished
        if is_processing_running_request or not is_item_in_queue(request_queue, DataTypes.REQUEST_RUNNING_DATA):
            request_queue.put(DataTypes.REQUEST_RUNNING_DATA)

    elif socket_data_type == DataTypes.REQUEST_DIRECTION_DATA:
        if not is_item_in_queue(request_queue, DataTypes.REQUEST_DIRECTION_DATA):
            request_queue.put(DataTypes.REQUEST_DIRECTION_DATA)

    elif socket_data_type == DataTypes.REQUEST_SUMMARY_DATA:
        image = running_data_handler.get_static_maps_image()
        running_data_handler.send_summary_data(CurrentData.exercise_type, CurrentData.start_place,
                                               CurrentData.start_time_string, CurrentData.curr_distance,
                                               CurrentData.avg_speed, total_sec, image)

    elif socket_data_type == DataTypes.REQUEST_RUNNING_DATA_UNIT:
        running_data_handler.send_running_unit("km", "bpm", "min/km")

    elif socket_data_type == DataTypes.REQUEST_SUMMARY_DATA_UNIT:
        running_data_handler.send_summary_unit(speed="min/km", distance="km")

    elif socket_data_type == DataTypes.REQUEST_TYPE_POSITION_MAPPING:
        running_data_handler.send_type_position_mapping()

    else:
        print(f'Unsupported data type: {socket_data_type}')


def get_training_update(training_mode, start_end_coords, training_speed=None):
    if training_mode == RunningTrainingMode.SpeedTraining:
        speed_training_update(start_end_coords, training_speed)
    elif training_mode == RunningTrainingMode.DistanceTraining:
        distance_training_update(start_end_coords)
    else:
        print('Unsupported training mode')


# assume training route is given as a list of coordinates
def speed_training_update(start_end_coords, training_speed):
    # FIXME: Implement this
    # decide the route
    # show all running info intermittently (say evey 400m for 5 seconds - customizable parameters)
    # show the running speed intermittently when it's higher/lower than the target speed (+ error) - const, may be give visual instructions also
    global is_processing_running_request

    while not request_queue.empty():
        if DataTypes.REQUEST_RUNNING_DATA in request_queue.queue:
            is_processing_running_request = True
            loop_speed_training(start_end_coords, training_speed)
            with request_queue.mutex:
                # print(str(list(request_queue.queue)))
                request_queue.queue.remove(DataTypes.REQUEST_RUNNING_DATA)
                is_processing_running_request = False

def loop_speed_training(start_end_coords, training_speed):
    global total_sec

    # check curr distance with prev distance > 400m every 5 seconds
    if (CurrentData.curr_distance - CurrentData.prev_distance) > SpeedTrainingStats.distance_interval:
        CurrentData.prev_distance = CurrentData.curr_distance
        for _ in range(SpeedTrainingStats.time_info_active):
            check_correct_speed(training_speed)
            running_data_handler.send_running_data(CurrentData.curr_distance, CurrentData.curr_heart_rate,
                                                   CurrentData.avg_speed, total_sec, True)
            time_utility.sleep_seconds(1) # update every second within 5 seconds
    else:
        for _ in range(SpeedTrainingStats.time_info_active):
            check_correct_speed(training_speed)
            if SpeedTrainingStats.correct_speed:
                running_data_handler.send_running_data()
                # TODO: maybe add an instruction to say user is on track?
            else:
                running_data_handler.send_running_data(speed=CurrentData.avg_speed)
            time_utility.sleep_seconds(1)


def check_correct_speed(training_speed):
    # check curr speed with target speed (+ error) every second
    SpeedTrainingStats.correct_speed = abs(
        CurrentData.avg_speed - training_speed) <= SpeedTrainingStats.training_speed_tolerance
    if SpeedTrainingStats.correct_speed and CurrentData.avg_speed != -1.0:
        running_data_handler.send_running_alert(speed="false")
    else:
        if CurrentData.avg_speed > training_speed or CurrentData.avg_speed == -1.0:
            instruction = "Speed up!"
        else:
            instruction = "Slow down!"
        running_data_handler.send_running_alert(speed="true", instruction=instruction)

def distance_training_update(start_end_coords):
    # FIXME: Implement this
    pass
