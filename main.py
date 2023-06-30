import threading
import modules.hololens.hololens_portal as hololens_portal
import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server
from collections import Counter
from modules.yolov8.VideoDetection import VideoDetection as YoloDetector
from modules.langchain_llm.LangChainTextGenerator import LangChainTextGenerator as TextGenerator
from services.running_service.running_service import get_exercise_data, start_training, RunningTrainingMode

flag_is_running = False


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()


def start_running_service():
    global flag_is_running
    training_mode = RunningTrainingMode.SpeedTraining
    training_route = []
    target_speed = 8  # min/km

    if flag_is_running:
        start_training(training_mode, training_route, target_speed)


def start_wearos(real_wearos):
    global flag_is_running

    while flag_is_running:
        get_exercise_data(real_wearos)


def start_wearos_threaded(wearos_real):
    server_thread = threading.Thread(target=start_wearos, args=(wearos_real,), daemon=True)
    server_thread.start()


def start_running_service_threaded():
    server_thread = threading.Thread(target=start_running_service, daemon=True)
    server_thread.start()


text_generator = TextGenerator(0)
translation_map = {}


def get_translation(object):
    global translation_map

    translation = translation_map.get(object)
    if translation is not None:
        return object + " - " + translation

    translation = text_generator.generate_response(
        "What is the Spanish translation of {input}? Provide only the answer.", object)
    translation_map[object] = translation
    return object + " - " + translation


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
            if detection_diff[item] <= -1:
                result += f'INSTRUCT|,'
            if detection_diff[item] >= 1:
                result += f'INSTRUCT|{get_translation(item)},'

        if result != '':
            send_socket_server(result)

        detection_init = detection_now

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

    start_running_service_threaded()

    start_yolo(hololens_portal.API_STREAM_VIDEO if hololens_real else 0)

    socket_server.stop_server_threaded()


_hololens = input("Hololens Real (e.g., 0/1)?")
_wearos = input("WearOS Real (e.g., 0/1)?")

run(_wearos == "1", _hololens == "1")
