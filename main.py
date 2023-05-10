import threading
import traceback
import sys
from collections import Counter
import random

import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server

from modules.yolov4.VideoCapture import VideoCapture as YoloDetector
import modules.hololens.hololens_portal as hololens_portal

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

    start_time = time_utility.get_current_millis();

    while flag_is_running:
        result = ''

        distance += (random.randint(1, 5) / 1000)
        result += f'DISTANCE|{round(distance, 2)} km,'

        heart_rate = random.randint(70,80)
        result += f'HR|{heart_rate} BPM,'

        time = time_utility.get_time_string("%I:%M %p")
        result += f'TIME|{time},'

        total_min = (time_utility.get_current_millis() - start_time) / (1000*60)
        speed = total_min / distance
        result += f'SPEED|{round(speed, 2)} min/km,'

        socket_data = get_socket_data()
        if "REQUEST_RUNNING_SUMMARY" == socket_data:
            result += f'DETAILS| Evening run,'
            result += f'AVG_SPEED|{round(speed, 2)} min/km,'
            result += f'TOT_DISTANCE|{round(distance, 2)} km,'
            result += 'TOT_TIME|{:02d}:{:02d},'.format(int(total_min), int((total_min % 1) * 60))

        if result != '':
            send_socket_server(result)

            # utilities.send_get_request(f'http://127.0.0.1:5050/?HR: {last_row_val}=1')
            # curl -X POST -d "" http://127.0.0.1:5050/?Hello=1

        time_utility.sleep_seconds(1)


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
        with YoloDetector(video_src, min_time=1) as yoloDetector:
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
