import threading
import random
import modules.hololens.hololens_portal as hololens_portal
import modules.websocket_server.socket_server as socket_server
import modules.utilities.time as time_utility
from modules.dataformat import finger_pose_data_pb2
import services.learning_service.learning_service as learning_service
from modules.yolov8.VideoDetection import VideoDetection as YoloDetector
from services.running_service.running_current_data import CurrentData
from services.running_service.running_service import get_exercise_data, get_training_update, RunningTrainingMode

flag_is_running = False
# based on the simulated route on wearOS, starts from Kings Cross station to Europcar Kings Cross in London.
training_route = [[51.530211685534, -0.12388666083292],
                  [51.53080391412693, -0.12166741887329217],
                  [51.531002439838325, -0.11902617965388047],
                  [51.53118923468958, -0.11651644992640586],
                  [51.531362914423525, -0.11416463561058425]]


def start_running_service(real_wearos):
    global flag_is_running, training_route
    training_mode = RunningTrainingMode.SpeedTraining
    target_speed = 8  # min/km

    while flag_is_running:
        get_training_update(training_mode, training_route, target_speed, real_wearos)


def start_wearos(real_wearos):
    global flag_is_running, training_route

    CurrentData.reset_values()

    if not real_wearos:
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


def start_learning_service(image_detector, pointing_real):
    global flag_is_running

    learning_service.configure_learning(image_detector)

    while flag_is_running:
        pointing_data = None

        if not pointing_real:
            if random.randint(0, 30) == 0:
                pointing_data = finger_pose_data_pb2.FingerPoseData(
                    camera_x=0.5,
                    camera_y=0.5,
                )

        learning_service.update_learning(pointing_data)


def start_learning_service_threaded(image_detector, pointing_real):
    server_thread = threading.Thread(target=start_learning_service,
                                     args=(image_detector, pointing_real,),
                                     daemon=True)
    server_thread.start()


def run(hololens_real=False, wearos_real=False, pointing_real=False):
    global flag_is_running

    flag_is_running = True
    socket_server.start_server_threaded()

    if wearos_real:
        start_wearos_threaded(wearos_real)
        start_running_service_threaded(wearos_real)

    video_src = hololens_portal.API_STREAM_VIDEO if hololens_real else 0

    with YoloDetector(video_src, save=False, inference=True, ) as yoloDetector:
        if not wearos_real:
            start_learning_service_threaded(yoloDetector, pointing_real)
        yoloDetector.start()

    socket_server.stop_server_threaded()


_hololens = input("Hololens Real (e.g., 0/1)?")
_wearos = input("WearOS Real (e.g., 0/1)?")
_pointing = input("Pointing Detection Real (e.g., 0/1)?")

run(_hololens == "1", _wearos == "1", _pointing == "1")
