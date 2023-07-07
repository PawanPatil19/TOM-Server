import threading
import modules.hololens.hololens_portal as hololens_portal
import modules.websocket_server.socket_server as socket_server
import modules.utilities.time as time_utility
from modules.yolov8.VideoDetection import VideoDetection as YoloDetector
from modules.langchain_llm.LangChainTextGenerator import LangChainTextGenerator as TextGenerator
from services.running_service.running_current_data import CurrentData
from services.running_service.running_service import get_exercise_data, get_training_update, RunningTrainingMode

flag_is_running = False
# based on the simulated route on wearOS, starts from Kings Cross station to Europcar Kings Cross in London.
training_route = [[51.530211685534, -0.12388666083292], [51.53080391412693, -0.12166741887329217],
                  [51.531002439838325, -0.11902617965388047], [51.53118923468958, -0.11651644992640586],
                  [51.531362914423525, -0.11416463561058425]]


def start_running_service(real_wearos):
    global flag_is_running, training_route
    training_mode = RunningTrainingMode.SpeedTraining
    target_speed = 8  # min/km

    while flag_is_running:
        get_training_update(training_mode, training_route, target_speed, real_wearos)


def start_wearos(real_wearos):
    global flag_is_running, training_route

    if not real_wearos:
        CurrentData.reset_values()
        CurrentData.start_time = time_utility.get_current_millis()

    while flag_is_running:
        get_exercise_data(real_wearos, training_route)


def start_wearos_threaded(wearos_real):
    server_thread = threading.Thread(
        target=start_wearos, args=(wearos_real,), daemon=True)
    server_thread.start()


def start_running_service_threaded(wearos_real):
    server_thread = threading.Thread(target=start_running_service, args=(wearos_real,), daemon=True)
    server_thread.start()


# text_generator = TextGenerator(0)
# translation_map = {}
#
#
# def get_translation(object):
#     global translation_map
#
#     translation = translation_map.get(object)
#     if translation is not None:
#         return object + " - " + translation
#
#     translation = text_generator.generate_response(
#         "What is the Spanish translation of {input}? Provide only the answer.", object)
#     translation_map[object] = translation
#     return object + " - " + translation


def start_yolo(video_src):
    global flag_is_running
    try:
        with YoloDetector(video_src, save=False) as yoloDetector:
            yoloDetector.start()
    except KeyboardInterrupt:
        print("Yolo module stopped")


def run(wearos_real=False, hololens_real=False):
    global flag_is_running

    flag_is_running = True
    socket_server.start_server_threaded()

    start_wearos_threaded(wearos_real)

    start_running_service_threaded(wearos_real)

    start_yolo(hololens_portal.API_STREAM_VIDEO if hololens_real else 0)

    socket_server.stop_server_threaded()


_hololens = input("Hololens Real (e.g., 0/1)?")
_wearos = input("WearOS Real (e.g., 0/1)?")

run(_wearos == "1", _hololens == "1")
