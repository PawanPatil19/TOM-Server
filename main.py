import threading
import traceback
import sys
from collections import Counter

import modules.fitbit_web.web_api as fitbit_web_api
import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server

from modules.yolov4.VideoCapture import VideoCapture as YoloDetector
import modules.hololens.hololens_portal as hololens_portal

flag_is_running = False


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def start_fitbit():
    global flag_is_running

    fitbit_credential = fitbit_web_api.read_fitbit_credential()
    fitbit_token = fitbit_web_api.read_fitbit_token()
    if fitbit_token is None:
        fitbit_token = fitbit_web_api.get_authorize_token(fitbit_credential)
        fitbit_web_api.save_fitbit_token(fitbit_token)

    fitbit_client = fitbit_web_api.get_auth_client(fitbit_credential, fitbit_token)
    today_string = time_utility.get_date_string("%Y-%m-%d")
    print(f'Today:{today_string}')

    # fitbit_raw_data_distance = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_DISTANCE, fitbit_web_api.DETAIL_LEVEL_1MIN)
    # print(f'\ndistance: {fitbit_raw_data_distance}')
    # 
    # fitbit_raw_data_steps = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_STEPS, fitbit_web_api.DETAIL_LEVEL_1MIN)
    # print(f'\nsteps: {fitbit_raw_data_steps}')

    current_millis_heart_rate = 0
    current_millis_steps = 0

    while flag_is_running:
        result = ''

        if time_utility.get_current_millis() - current_millis_heart_rate > 10 * 1000:
            try:
                fitbit_raw_data_heart_rate = fitbit_web_api.get_json_data(fitbit_client, today_string,
                                                                          fitbit_web_api.DATA_TYPE_HEART_RATE,
                                                                          fitbit_web_api.DETAIL_LEVEL_1SEC)
                # print(fitbit_raw_data_heart_rate)
                df = fitbit_web_api.get_data_frame(fitbit_raw_data_heart_rate, fitbit_web_api.DATA_TYPE_HEART_RATE)
                result += f'HR|{df.iloc[-1]["value"]},'
            except Exception:
                traceback.print_exc(file=sys.stdout)

            current_millis_heart_rate = time_utility.get_current_millis()

        if time_utility.get_current_millis() - current_millis_steps > 60 * 1000:
            try:
                fitbit_raw_data_steps = fitbit_web_api.get_json_data(fitbit_client, today_string,
                                                                     fitbit_web_api.DATA_TYPE_STEPS,
                                                                     fitbit_web_api.DETAIL_LEVEL_1MIN)
                df = fitbit_web_api.get_data_frame(fitbit_raw_data_steps, fitbit_web_api.DATA_TYPE_STEPS)
                result += f'STEPS|{df.iloc[-1]["value"]},'
            except Exception:
                traceback.print_exc(file=sys.stdout)

            current_millis_steps = time_utility.get_current_millis()

        if result != '':
            send_socket_server(result)

            # utilities.send_get_request(f'http://127.0.0.1:5050/?HR: {last_row_val}=1')
            # curl -X POST -d "" http://127.0.0.1:5050/?Hello=1 

        time_utility.sleep_seconds(1)


def start_fitbit_threaded():
    server_thread = threading.Thread(target=start_fitbit, daemon=True)
    server_thread.start()


def start_timer():
    global flag_is_running

    t = 0
    while flag_is_running:
        t += 1
        mins, secs = divmod(t, 60)
        send_socket_server('TIME|{:02d}:{:02d}'.format(mins, secs))
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
            if detection_diff[item] >= min_detection_count:
                result += f'DETECT|{item},'
            elif detection_diff[item] <= -min_detection_count:
                result += f'UNDETECT|{item},'

        if result != '':
            send_socket_server(result)

        detection_init = detection_now

        time_utility.sleep_seconds(min_gap)


def start_yolo():
    global flag_is_running

    # video_src = hololens_portal.API_STREAM_VIDEO 
    video_src = 0

    try:
        with YoloDetector(video_src, min_time=1) as yoloDetector:
            threading.Thread(target=_monitor_yolo_detection, args=(yoloDetector, 1,), daemon=True).start()
            yoloDetector.start()
    except KeyboardInterrupt:
        print("Yolo module stopped")


def run():
    global flag_is_running

    flag_is_running = True
    socket_server.start_server_threaded()

    # start_fitbit_threaded()
    start_timer_threaded()
    # start_yolo()

    socket_server.stop_server_threaded()


run()
