from enum import Enum
from queue import Queue

import modules.utilities.time as time_utility
from config import DIRECTIONS_OPTION, ORS_OPTION
from modules.dataformat.data_types import DataTypes
from modules.maps.maps_util import get_direction_str
from services.running_service.running_current_data import CurrentData
from . import running_data_handler as running_data_handler


class RunningTrainingMode(Enum):
    SpeedTraining = 0
    DistanceTraining = 1


class SpeedTrainingStats:
    distance_interval = 0.4  # km
    # number of times to update running data before checking for distance 
    # (e.g. running data updated 5 times before checking if distance > 400m)
    num_running_iterations = 5
    update_interval_running = 1  # secs
    update_interval_direction = 5  # secs
    training_speed_tolerance = 0.5  # min/km
    direction_distance_tolerance = 20  # m
    correct_speed = False


total_sec = 0
request_queue = Queue()
running_update_count = 0
dist_check = False
latest_start_time = 0.0
waypoint_radius = 20  # meters
dest_radius = 10  # meters


def is_item_in_queue(item):
    global request_queue
    with request_queue.mutex:
        return item in request_queue.queue


def get_exercise_data(real_wearos, training_route):
    global total_sec
    total_sec = (time_utility.get_current_millis() - CurrentData.start_time) / 1000
    total_min = (total_sec / 60)

    # receive data from Unity or WearOS client
    socket_data = running_data_handler.get_socket_data()

    # mock service
    if not real_wearos:
        running_data_handler.save_mock_running_data(total_min)
        running_data_handler.save_mock_coords(training_route)

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
        print('received running request')
        # put request in queue to be processed later when speed or distance training is started
        request_queue.put(DataTypes.REQUEST_RUNNING_DATA)

    elif socket_data_type == DataTypes.REQUEST_DIRECTION_DATA:
        print('received direction request')
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
    global running_update_count, dist_check

    CurrentData.curr_route = training_route
    dist_check = False

    while True:
        if DataTypes.REQUEST_RUNNING_DATA in request_queue.queue:
            running_update_count += 1
            if running_update_count == SpeedTrainingStats.num_running_iterations:
                running_update_count = 0
                dist_check = (CurrentData.curr_distance - CurrentData.prev_distance) > SpeedTrainingStats.distance_interval
                if dist_check:
                    CurrentData.prev_distance = CurrentData.curr_distance

            process_running_request(training_speed)
            with request_queue.mutex:
                request_queue.queue.remove(DataTypes.REQUEST_RUNNING_DATA)

        if DataTypes.REQUEST_DIRECTION_DATA in request_queue.queue:
            process_direction_request(real_wearos)
            with request_queue.mutex:
                request_queue.queue.remove(DataTypes.REQUEST_DIRECTION_DATA)
        time_utility.sleep_seconds(0.2)


def process_running_request(training_speed):
    global dist_check
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


def process_direction_request(real_wearos):
    print('Processing direction data...')
    if real_wearos:
        if CurrentData.curr_lat == 0.0 and CurrentData.curr_lng == 0.0:
            CurrentData.curr_lat = CurrentData.curr_route[0][0]
            CurrentData.curr_lng = CurrentData.curr_route[0][1]
        else:
            # remove first coordinate with current coordinate
            CurrentData.curr_route.pop(0)
            CurrentData.curr_route.insert(0, [CurrentData.curr_lat, CurrentData.curr_lng])

        result = running_data_handler.get_directions_real(CurrentData.start_time, CurrentData.curr_route,
                                                          CurrentData.bearing, DIRECTIONS_OPTION, ORS_OPTION)
    else:
        result = running_data_handler.get_directions_mock(total_sec)
    parse_direction_result(result)


def parse_direction_result(result):
    global latest_start_time, waypoint_radius
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
        CurrentData.total_steps = int(num_steps)

    # if the user walks the wrong way, the total steps will be less than the current steps
    # so we need to update the total steps to the current steps
    if CurrentData.curr_steps > CurrentData.total_steps:
        CurrentData.total_steps = int(num_steps)

    # Update number of current steps
    CurrentData.curr_steps = int(num_steps)

    # if user is near waypoint, waypoint is considered to have been reached and remove waypoint from route
    # print("Waypoint distance: " + waypoint_dist_str)
    if waypoint_dist <= waypoint_radius and len(CurrentData.curr_route) > 2:
        print("Waypoint reached, removing waypoint from route")
        CurrentData.curr_route.pop(1)

    send_direction_data(dest_dist, dest_dist_str, dest_duration_str, curr_dist, curr_dist_str, curr_duration_str,
                        curr_instr, curr_direction)


def send_direction_data(dest_dist, dest_dist_str, dest_duration_str, curr_dist, curr_dist_str, curr_duration_str,
                        curr_instr, curr_direction):
    # we set a 5 meters radius from destination for the user to be considered to have reached destination
    if CurrentData.curr_steps == 1 and dest_dist <= dest_radius:
        print("Destination distance: " + dest_dist_str)
        running_data_handler.send_direction_data(curr_instr="Destination Reached!")

    # check for first and last, always show direction data
    elif CurrentData.curr_steps == 1 or CurrentData.curr_steps == CurrentData.total_steps:
        print("curr_steps: " + str(CurrentData.curr_steps) + ", total_steps: " + str(CurrentData.total_steps))
        running_data_handler.send_direction_data(dest_dist_str, dest_duration_str, curr_dist_str, curr_duration_str,
                                                 curr_instr, curr_direction)

    # check for direction, don't show if straight
    elif get_direction_str(curr_direction) != "straight":
        print("curr_direction: " + get_direction_str(curr_direction))
        # check for distance, only show if close by like x meters for example
        if curr_dist <= SpeedTrainingStats.direction_distance_tolerance:
            print("curr_dist: " + curr_dist_str)
            running_data_handler.send_direction_data(dest_dist_str, dest_duration_str, curr_dist_str, curr_duration_str,
                                                     curr_instr, curr_direction)
        else:
            # hide direction data
            running_data_handler.send_direction_data()
    else:
        running_data_handler.send_direction_data()


def distance_training_update(training_route):
    # FIXME: Implement this
    pass
