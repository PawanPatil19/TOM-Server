import threading
import random

import modules.hololens.hololens_portal as hololens_portal
import modules.websocket_server.socket_server as socket_server
from modules.dataformat import finger_pose_data_pb2
import services.learning_service.learning_service as learning_service
from modules.yolov8.VideoDetection import VideoDetection as YoloDetector

flag_is_running = False


def start_learning_service(image_detector, pointing_real):
    global flag_is_running

    learning_service.configure_learning(image_detector)

    while flag_is_running:
        pointing_data = None

        if not pointing_real:
            if random.randint(0, 20) == 0:
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


def run(hololens_real=False, pointing_real=False):
    global flag_is_running

    flag_is_running = True
    socket_server.start_server_threaded()

    video_src = hololens_portal.API_STREAM_VIDEO if hololens_real else 0

    with YoloDetector(video_src, save=False) as yoloDetector:
        start_learning_service_threaded(yoloDetector, pointing_real)
        yoloDetector.start()

    socket_server.stop_server_threaded()


_hololens = input("Hololens Real (e.g., 0/1)?")
_pointing = input("Pointing Detection Real (e.g., 0/1)?")

run(_hololens == "1", _pointing == "1")
