import random
import threading
from collections import Counter
from google.protobuf.message import DecodeError

import modules.google_api.google_api as google_api
import modules.hololens.hololens_portal as hololens_portal
import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server
from modules.dataformat import exercise_client_data_pb2
from modules.dataformat import exercise_sensor_data_pb2
from modules.dataformat import socket_data_pb2
from modules.dataformat import summary_data_pb2
from modules.dataformat.data_types import DataTypes
from modules.yolov8.VideoDetection import VideoDetection as YoloDetector

flag_is_running = False


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()


def start_wearos(real_wearos):
    global flag_is_running

    curr_heart_rate = 0
    curr_distance = 0.0
    avg_speed = 0.0
    src_lat = 0.0
    src_lng = 0.0
    dest_lat = 0.0
    dest_lng = 0.0

    start_time = time_utility.get_current_millis()
    start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
    start_place = 'NUS'

    start_place_lat = 1.294791
    start_place_lng = 103.7609882
    temp_count = 0

    while flag_is_running:
        total_sec = (time_utility.get_current_millis() - start_time) / 1000
        total_min = total_sec / 60
        curr_time = time_utility.get_current_millis()

        # receive data from Unity or WearOS client
        socket_data = get_socket_data()

        # mock service
        if not real_wearos:
            temp_count += 1
            curr_distance += (random.randint(1, 5) / 1000) # in km
            curr_heart_rate = random.randint(70, 80)
            avg_speed = total_min / curr_distance
            if src_lat == 0.0 and src_lng == 0.0: 
                src_lat = start_place_lat
                src_lng = start_place_lng
            dest_lat = src_lat + temp_count * 0.000015
            dest_lng = src_lng + temp_count * 0.000015
            send_exercise_client_data_to_unity(curr_distance, int(curr_heart_rate), avg_speed, curr_time, int(total_sec))

        # skip if no data
        if socket_data is None:
            time_utility.sleep_seconds(0.5)
            continue

        # actual data
        if real_wearos:
            exercise_sensor_data = get_decoded_wearos_data(socket_data)

            if exercise_sensor_data is not None:
                avg_speed = 0.0
                if exercise_sensor_data.speed_avg > 0:
                    avg_speed = 1000 / (60 * exercise_sensor_data.speed_avg)  # min/km
                curr_distance = exercise_sensor_data.distance / 1000  # km
                curr_heart_rate = exercise_sensor_data.heart_rate
                if not (exercise_sensor_data.latitude == 0.0 and exercise_sensor_data.longitude == 0.0):
                    if src_lat == 0.0 and src_lng == 0.0: 
                        src_lat = exercise_sensor_data.latitude
                        src_lng = exercise_sensor_data.longitude
                    dest_lat = exercise_sensor_data.latitude
                    dest_lng = exercise_sensor_data.longitude

                send_exercise_client_data_to_unity(curr_distance, int(curr_heart_rate), avg_speed, curr_time, int(total_sec))

        if "REQUEST_RUNNING_SUMMARY" == socket_data:
            summary_data_proto = summary_data_pb2.SummaryData(
                details = f'Morning Run at {start_place} on {start_time_string}',
                total_distance = curr_distance,
                avg_speed = avg_speed,
                total_duration = int(total_sec),
                src_lat = src_lat,
                src_lng = src_lng,
                dest_lat = dest_lat,
                dest_lng = dest_lng
            )
            summary_bytes = wrap_message_with_metadata(summary_data_proto, DataTypes.SUMMARY_DATA)
            send_socket_server(summary_bytes)

        if "REQUEST_GOOGLE_MAP_API_KEY" == socket_data:
            result = f'GOOGLE_MAP_API_KEY|{google_api.get_google_credential(google_api.KEY_MAP_API)},'
            send_socket_server(result)



def send_exercise_client_data_to_unity(total_distance, curr_heart_rate, avg_speed, curr_time, exercise_duration):
    exercise_client_data_proto = exercise_client_data_pb2.ExerciseClientData(
        total_distance = total_distance,
        curr_heart_rate = curr_heart_rate,
        avg_speed = avg_speed,
        curr_time = curr_time,
        exercise_duration = exercise_duration,
    )
    exercise_client_bytes = wrap_message_with_metadata(exercise_client_data_proto, DataTypes.EXERCISE_CLIENT_DATA)
    # send the data back to Unity client
    send_socket_server(exercise_client_bytes)


def wrap_message_with_metadata(data, data_type):
    socket_data = socket_data_pb2.SocketData(
        data_type = data_type,
        data = data.SerializeToString()
    )

    return socket_data.SerializeToString()


def get_decoded_wearos_data(socket_data):
    if socket_data is None or isinstance(socket_data, str):
        return None

    try:
        # Attempt to parse the received data as socket_data protobuf 
        socket_data_msg = socket_data_pb2.SocketData()
        socket_data_msg.ParseFromString(socket_data)

        data_type = socket_data_msg.data_type
        data = socket_data_msg.data

        # Check if data received is exercise_sensor_data protobuf type
        if data_type == DataTypes.EXERCISE_SENSOR_DATA:
            try:
                exercise_sensor_data = exercise_sensor_data_pb2.ExerciseSensorData()
                exercise_sensor_data.ParseFromString(data)

                return exercise_sensor_data
            except DecodeError:
                # Not a valid exercise_sensor_data protobuf message
                return None
        else:
            # Not an exercise_sensor_data protobuf message
            return None
    except DecodeError:
        # Not a valid socket_data protobuf message
        return None


last_update_time = 0
next_reset_time = 0
reset_direction = False


def get_directions(total_sec):
    global last_update_time, next_reset_time, reset_direction

    directions = ''

    if total_sec > last_update_time + 25:
        rand_dir = random.randint(1, 3)
        if rand_dir == 1:
            directions = 'ANGLE|0,INSTRUCT|Turn Left,'
        elif rand_dir == 2:
            directions = 'ANGLE|90,INSTRUCT|Go Strait,'
        elif rand_dir == 3:
            directions = 'ANGLE|180,INSTRUCT|Turn Right,'
        else:
            directions = ''

        last_update_time = total_sec
        reset_direction = False
        next_reset_time = last_update_time + 3

    if total_sec > next_reset_time and not reset_direction:
        directions = 'ANGLE|-1,INSTRUCT|,'
        reset_direction = True

    return directions


def start_wearos_threaded(wearos_real):
    server_thread = threading.Thread(target=start_wearos, args=(wearos_real,), daemon=True)
    server_thread.start()


def _monitor_yolo_detection(detector, min_detection_count_percentage=0.6, update_gap=1):
    global flag_is_running

    detection_init = Counter()

    while flag_is_running:
        detections = detector.get_detect_object_percentage()

        detected_objects = [key for key, value in detections.items() if
                            value > min_detection_count_percentage]

        detection_now = Counter(detected_objects)
        detection_diff = Counter(detection_now)
        detection_diff.subtract(detection_init)

        print(detection_diff)

        result = ''

        for item in detection_diff:
            # if detection_diff[item] <= -1:
            #     result += f'INSTRUCT|,'
            if detection_diff[item] >= 1:
                result += f'INSTRUCT|{item},'

        if result != '':
            send_socket_server(result)

        detection_init = detection_now
        #
        time_utility.sleep_seconds(update_gap)


def start_yolo(video_src):
    global flag_is_running

    try:
        with YoloDetector(video_src, save=False) as yoloDetector:
            threading.Thread(target=_monitor_yolo_detection, args=(yoloDetector, 0.6, 1,),
                             daemon=True).start()
            yoloDetector.start()
    except KeyboardInterrupt:
        print("Yolo module stopped")


def run(wearos_real=False, hololens_real=False):
    global flag_is_running

    flag_is_running = True
    socket_server.start_server_threaded()

    start_wearos_threaded(wearos_real)

    start_yolo(hololens_portal.API_STREAM_VIDEO if hololens_real else 0)

    socket_server.stop_server_threaded()


_hololens = input("Hololens Real (e.g., 0/1)?")
_wearos = input("WearOS Real (e.g., 0/1)?")

run(_wearos == "1", _hololens == "1")
