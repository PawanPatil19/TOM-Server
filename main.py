﻿import threading
import traceback
import sys
from collections import Counter
import random

import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server

from modules.yolov8.VideoDetection import VideoDetection as YoloDetector
import modules.hololens.hololens_portal as hololens_portal

import modules.google_api.google_api as google_api

flag_is_running = False


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()




def start_wearos():
    global flag_is_running

    heart_rate = 0
    distance = 0
    time = ""

    start_time = time_utility.get_current_millis()
    start_time_string = time_utility.get_date_string("%d %B %I:%M %p")
    start_place = 'NUS'



    while flag_is_running:
        result = ''

        distance += (random.randint(1, 5) / 1000)
        result += f'DISTANCE|{round(distance, 2)} km,'

        heart_rate = random.randint(70,80)
        result += f'HR|{heart_rate} BPM,'

        time = time_utility.get_time_string("%I:%M %p")
        result += f'TIME|{time},'

        total_sec = (time_utility.get_current_millis() - start_time) / 1000
        total_min = total_sec / 60
        speed = total_min / distance
        result += f'SPEED|{round(speed, 2)} min/km,'

        # directions
        result += get_directions(total_sec)

        socket_data = get_socket_data()
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

def start_wearos_threaded():
    server_thread = threading.Thread(target=start_wearos, daemon=True)
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


def _monitor_yolo_detection(detector, min_gap, min_detection_count=3):
    global flag_is_running

    detection_init = Counter()

    while flag_is_running:
        detections = detector.get_detected_objects()
        # print(f'Detected: {detections}')
        # TODO: multiple detection
        filtered_detections = [j for sub in detections for j in sub if j != 'NaN']
        detection_now = Counter(filtered_detections)
        detection_diff = Counter(detection_now)
        detection_diff.subtract(detection_init)

        print(detection_diff)
        result = ''
        for item in detection_diff:
            # if detection_diff[item] <= -min_detection_count:
            #     # result += f'UNDETECT|{item},'
            #     result += f'INSTRUCT|,'
            if detection_diff[item] >= min_detection_count:
                result += f'INSTRUCT|{item},'
            
        if result != '':
            send_socket_server(result)

        detection_init = detection_now

        time_utility.sleep_seconds(min_gap)


def start_yolo(video_src):
    global flag_is_running

    try:
        with YoloDetector(video_src, save = False) as yoloDetector:
            threading.Thread(target=_monitor_yolo_detection, args=(yoloDetector, 1,), daemon=True).start()
            yoloDetector.start()
    except KeyboardInterrupt:
        print("Yolo module stopped")


def run(wearos=False, hololens=False):
    global flag_is_running

    flag_is_running = True
    socket_server.start_server_threaded()

    start_timer_threaded()

    if wearos:
        start_wearos_threaded()

    if hololens:
        start_yolo(hololens_portal.API_STREAM_VIDEO)
    else:
        start_yolo(0)
    # time_utility.sleep_seconds(10)
    
    socket_server.stop_server_threaded()


_hololens = input("Hololens (e.g., 0/1)?")
_wearos = input("Wearos (e.g., 0/1)?")

run(_wearos == "1", _hololens == "1")
