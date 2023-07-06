from queue import Queue
from enum import Enum
import threading

import modules.utilities.time as time_utility
from config import DIRECTIONS_OPTION, ORS_OPTION
from modules.dataformat.data_types import DataTypes
from services.running_service.running_current_data import CurrentData
from . import running_data_handler as running_data_handler


class RunningTrainingMode(Enum):
    SpeedTraining = 0
    DistanceTraining = 1


class SpeedTrainingStats:
    distance_interval = 0.4  # km
    time_info_active = 5  # secs
    update_interval = 1  # secs
    training_speed_tolerance = 0.5  # min/km
    direction_distance_tolerance = 20  # m
    correct_speed = False


total_sec = 0
request_queue = Queue()
is_processing_running = False
is_processing_direction = False
has_running = False
has_direction = False
latest_start_time = 0.0
waypoint_radius = 20  # meters
destination_radius = 10  # meters


def is_item_in_queue(queue, item):
    with queue.mutex:
        return item in queue.queue


def get_exercise_data(real_wearos):
    global total_sec, has_running, has_direction
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
        if is_processing_running or not is_item_in_queue(request_queue, DataTypes.REQUEST_RUNNING_DATA):
            print('received running request')
            request_queue.put(DataTypes.REQUEST_RUNNING_DATA)
            has_running = True

    elif socket_data_type == DataTypes.REQUEST_DIRECTION_DATA:
        if is_processing_direction or not is_item_in_queue(request_queue, DataTypes.REQUEST_DIRECTION_DATA):
            print('received direction request')
            request_queue.put(DataTypes.REQUEST_DIRECTION_DATA)
            has_direction = True

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


def get_training_update(training_mode, training_route, training_speed=None, real_wearos=False):
    if training_mode == RunningTrainingMode.SpeedTraining:
        speed_training_update(training_route, training_speed, real_wearos)
    elif training_mode == RunningTrainingMode.DistanceTraining:
        distance_training_update(training_route)
    else:
        print('Unsupported training mode')


# assume training route is given as a list of coordinates
def speed_training_update(training_route, training_speed, real_wearos):
    # FIXME: Implement this decide the route show all running info intermittently (say evey 400m for 5 seconds -
    #  customizable parameters) show the running speed intermittently when it's higher/lower than the target speed (+
    #  error) - const, may be give visual instructions also
    global is_processing_running, is_processing_direction, has_running, has_direction

    CurrentData.curr_route = training_route

    while True:
        if has_running or has_direction in request_queue.queue:
            # print(str(list(request_queue.queue)))
            loop_speed_training(training_speed, real_wearos)
            with request_queue.mutex:
                if has_running:
                    request_queue.queue.remove(DataTypes.REQUEST_RUNNING_DATA)
                    is_processing_running = False
                    has_running = DataTypes.REQUEST_RUNNING_DATA in request_queue.queue
                if has_direction:
                    request_queue.queue.remove(DataTypes.REQUEST_DIRECTION_DATA)
                    is_processing_direction = False
                    has_direction = DataTypes.REQUEST_DIRECTION_DATA in request_queue.queue


def loop_speed_training(training_speed, real_wearos):
    global total_sec, is_processing_running, is_processing_direction, has_running, has_direction

    # check curr distance with prev distance > 400m every 5 seconds
    dist_check = (CurrentData.curr_distance - CurrentData.prev_distance) > SpeedTrainingStats.distance_interval
    if has_running:
        is_processing_running = True
        if dist_check:
            CurrentData.prev_distance = CurrentData.curr_distance

    for _ in range(SpeedTrainingStats.time_info_active):
        threads = []

        if has_running:
            running_thread = threading.Thread(target=process_running_request, args=(training_speed, dist_check))
            threads.append(running_thread)
            running_thread.start()

        if has_direction:
            direction_thread = threading.Thread(target=process_direction_request, args=(real_wearos, ))
            threads.append(direction_thread)
            direction_thread.start()

        for thread in threads:
            thread.join()

        time_utility.sleep_seconds(SpeedTrainingStats.update_interval)


def process_running_request(training_speed, dist_check):
    print('Processing running data...')
    check_correct_speed(training_speed)
    if dist_check:
        running_data_handler.send_running_data(CurrentData.curr_distance, CurrentData.curr_heart_rate,
                                               CurrentData.avg_speed, total_sec, True)
    else:
        if SpeedTrainingStats.correct_speed:
            # TODO: maybe add an instruction to say user is on track?
            running_data_handler.send_running_data()
        else:
            running_data_handler.send_running_data(speed=CurrentData.avg_speed)


def process_direction_request(real_wearos):
    print('Processing direction data...')
    global latest_start_time, waypoint_radius
    if real_wearos:
        if CurrentData.curr_lat == 0.0 and CurrentData.curr_lng == 0.0:
            CurrentData.curr_lat = CurrentData.curr_route[0][0]
            CurrentData.curr_lng = CurrentData.curr_route[0][1]
        else:
            # remove first coordinate with current coordinate
            print("Before remove: " + str(CurrentData.curr_route))
            CurrentData.curr_route.pop(0)
            CurrentData.curr_route.insert(0, [CurrentData.curr_lat, CurrentData.curr_lng])
            print("After remove: " + str(CurrentData.curr_route))

        result = running_data_handler.get_directions_real(CurrentData.start_time, CurrentData.curr_route,
                                                          CurrentData.bearing, DIRECTIONS_OPTION, ORS_OPTION)
    else:
        result = running_data_handler.get_directions_mock(total_sec)

    # result can't be None, it just returns empty DirectionData if no data
    # so no need to check if result is None
    dest_dist_str = result.dest_dist_str
    dest_dist = result.dest_dist
    dest_duration_str = result.dest_duration_str
    dest_duration = result.dest_duration
    curr_dist_str = result.curr_dist_str
    curr_dist = result.curr_dist
    curr_duration_str = result.curr_duration_str
    curr_duration = result.curr_duration
    curr_instr = result.curr_instr
    curr_direction = result.curr_direction
    num_steps = result.num_steps
    waypoint_dist = result.waypoint_dist
    waypoint_dist_str = result.waypoint_dist_str
    waypoint_duration = result.waypoint_duration
    waypoint_duration_str = result.waypoint_duration_str

    # Check if CurrentData is a new exercise/route (use start time to differentiate)
    if latest_start_time != CurrentData.start_time:
        latest_start_time = CurrentData.start_time
        # set total steps count to new route steps count
        # print("total_steps: " + num_steps)
        CurrentData.total_steps = int(num_steps)

    # if the user walks the wrong way, the total steps will be less than the current steps
    # so we need to update the total steps to the current steps
    if CurrentData.curr_steps > CurrentData.total_steps:
        CurrentData.total_steps = int(num_steps)

    CurrentData.curr_steps = int(num_steps)

    # if user is near waypoint, waypoint is considered to have been reached and remove waypoint from route
    print("Waypoint distance: " + str(waypoint_dist))
    if waypoint_dist <= waypoint_radius and len(CurrentData.curr_route) > 2:
        print("waypoint reached")
        CurrentData.curr_route.pop(1)

    # we set a 5 meters radius from destination for the user to be considered to have reached destination
    if CurrentData.curr_steps == 1 and CurrentData.curr_distance <= destination_radius:
        running_data_handler.send_direction_data(curr_instr="Destination Reached!")

    # check for first and last, always show direction data
    elif CurrentData.curr_steps == 1 or CurrentData.curr_steps == CurrentData.total_steps:
        # print("curr_steps: " + str(CurrentData.curr_steps) + ", total_steps: " + str(CurrentData.total_steps))
        running_data_handler.send_direction_data(dest_dist_str, dest_duration_str, curr_dist_str, curr_duration_str,
                                                 curr_instr, curr_direction)

    # check for direction, don't show if straight
    elif curr_direction != "straight":
        # print("curr_direction: " + curr_direction)
        # check for distance, only show if close by like x meters for example
        if curr_dist <= SpeedTrainingStats.direction_distance_tolerance:
            # print("curr_dist: " + curr_dist_str)
            running_data_handler.send_direction_data(dest_dist_str, dest_duration_str, curr_dist_str, curr_duration_str,
                                                     curr_instr, curr_direction)
        else:
            # hide direction data
            running_data_handler.send_direction_data()
    else:
        running_data_handler.send_direction_data()


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
