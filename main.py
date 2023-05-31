import random
import threading
from collections import Counter
from google.protobuf.message import DecodeError

import modules.google_api.google_api as google_api
import modules.hololens.hololens_portal as hololens_portal
import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server
from modules.dataformat import exercise_data_pb2
from modules.dataformat import socket_data_pb2
from modules.yolov8.VideoDetection import VideoDetection as YoloDetector

flag_is_running = False


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()


def start_wearos(real_wearos):
    global flag_is_running

    heart_rate = 0
    distance = 0
    time = ""

    start_time = time_utility.get_current_millis()
    start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
    start_place = 'NUS'

    while flag_is_running:
        result = ''

        total_sec = (time_utility.get_current_millis() - start_time) / 1000
        total_min = total_sec / 60

        # receive data from Unity or WearOS client
        socket_data = get_socket_data()

        # mock service
        if not real_wearos:
            distance += (random.randint(1, 5) / 1000)
            result += f'DISTANCE|{round(distance, 2)} km,'

            heart_rate = random.randint(70, 80)
            result += f'HR|{heart_rate} BPM,'

            time = time_utility.get_time_string("%I:%M %p")
            result += f'TIME|{time},'

            speed = total_min / distance
            result += f'SPEED|{round(speed, 2)} min/km,'

            # directions
            result += get_directions(total_sec)
        else:
            exercise_data = get_decoded_wearos_data(socket_data)

            if exercise_data is not None:
                speed = 0
                if (exercise_data.speed_avg > 0):
                    speed = 1000 / (60 * exercise_data.speed_avg)  # min/km
                distance = exercise_data.distance / 1000  # km

                start_time = exercise_data.start_time
                update_time = exercise_data.update_time
                duration = exercise_data.duration
                latitude = exercise_data.latitude
                longitude = exercise_data.longitude
                distance = exercise_data.distance
                calories = exercise_data.calories
                heart_rate = exercise_data.heart_rate
                heart_rate_avg = exercise_data.heart_rate_avg
                speed = exercise_data.speed
                speed_avg = exercise_data.speed_avg
                exercise_type = exercise_data.exercise_type

                print(
                f'Received data: \n Start Time:{start_time} \n Update Time:{update_time} \n '
                f'Duration:{duration} \n Latitude:{latitude} \n Longitude:{longitude} \n Distance:{distance} \n '
                f'Calories:{calories} \n Heart Rate:{heart_rate} \n Heart Rate Avg:{heart_rate_avg} \n Speed:{speed} '
                f'\n Speed Avg:{speed_avg} \n Exercise Type:{exercise_type} \n ')

                # send the data back to Unity client
                send_socket_server(socket_data)
            else:
                speed = 0
                distance = 0

        if "REQUEST_RUNNING_SUMMARY" == socket_data:
            result += f'DETAILS| Morning Run at {start_place} on {start_time_string},'
            result += f'AVG_SPEED|{round(speed, 2)} min/km,'
            result += f'TOT_DISTANCE|{round(distance, 2)} km,'
            result += 'TOT_TIME|{:02d}:{:02d},'.format(int(total_min), int((total_min % 1) * 60))

        if "REQUEST_GOOGLE_MAP_API_KEY" == socket_data:
            result += f'GOOGLE_MAP_API_KEY|{google_api.get_google_credential(google_api.KEY_MAP_API)},'

        if result != '':
            send_socket_server(result)

        # utilities.send_get_request(f'http://127.0.0.1:5050/?HR: {last_row_val}=1')
        # curl -X POST -d "" http://127.0.0.1:5050/?Hello=1

        time_utility.sleep_seconds(1)


def get_decoded_wearos_data(socket_data):
    if socket_data is None or isinstance(socket_data, str):
        return None

    try:
        # Attempt to parse the received data as socket_data protobuf 
        socket_data_msg = socket_data_pb2.SocketData()
        socket_data_msg.ParseFromString(socket_data)

        data_type = socket_data_msg.data_type
        data = socket_data_msg.data

        # Check if data received is exercise_data protobuf type
        if data_type == "EXERCISE_DATA":
            try:
                exercise_data = exercise_data_pb2.ExerciseData()
                exercise_data.ParseFromString(data)

                return exercise_data
            except DecodeError:
                # Not a valid exercise_data protobuf message
                return None
        else:
            # Not an exercise_data protobuf message
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


def start_timer():
    global flag_is_running

    t = 0
    while flag_is_running:
        t += 1
        mins, secs = divmod(t, 60)
        send_socket_server('TIMER|{:02d}:{:02d},'.format(mins, secs))
        time_utility.sleep_seconds(1)


def start_timer_threaded():
    threading.Thread(target=start_timer, daemon=True).start()


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

    start_timer_threaded()

    start_wearos_threaded(wearos_real)

    start_yolo(hololens_portal.API_STREAM_VIDEO if hololens_real else 0)

    socket_server.stop_server_threaded()


_hololens = input("Hololens Real (e.g., 0/1)?")
_wearos = input("WearOS Real (e.g., 0/1)?")

run(_wearos == "1", _hololens == "1")
