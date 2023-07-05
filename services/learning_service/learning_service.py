from enum import Enum

import math
import statistics
import modules.utilities.time as time_utility
from modules.dataformat.data_types import DataTypes
from . import learning_data_handler as learning_data_handler

from modules.yolov8.VideoDetection import VideoDetection as YoloDetector
from modules.langchain_llm.LangChainTextGenerator import LangChainTextGenerator as TextGenerator


class LearningConfig:
    finger_pointing_trigger_duration = 2  # seconds
    finger_pointing_location_offset = 0.1  # 10% of the screen width/height
    finger_detection_duration = 1  # seconds (depends on the client)
    finger_pointing_buffer_size = math.ceil(
        finger_pointing_trigger_duration / finger_detection_duration)


_text_generator = None
_learning_map = {}

_image_detector = None
_finger_pose_buffer = []


def _get_text_generator():
    global _text_generator

    if _text_generator is None:
        _text_generator = TextGenerator(0)

    return _text_generator


def get_learning_data(object_of_interest):
    global _learning_map

    learning_content = _learning_map.get(object_of_interest)

    if learning_content is not None:
        return learning_content

    text_generator = _get_text_generator()
    learning_content = text_generator.generate_response(
        "Briefly describe *{input}* in one sentence? Provide only the answer.",
        object_of_interest
    )
    _learning_map[object_of_interest] = learning_content

    return learning_content


def _handle_learning_requests(finger_pointing_data = None):

    # handle finger pointing data
    if finger_pointing_data is not None:
        _handle_finger_pose(finger_pointing_data)

    # handle learning requests from socket
    socket_data = learning_data_handler.get_socket_data()
    # skip if no data
    if socket_data is None:
        time_utility.sleep_seconds(0.3)
        return

    # decode data
    socket_data_type, decoded_data = learning_data_handler.get_decoded_socket_data(socket_data)
    if socket_data_type is None:
        return

    if socket_data_type == DataTypes.FINGER_POINTING_DATA:
        finger_pose_data = learning_data_handler.decode_finger_pose_data(decoded_data)
        _handle_finger_pose(finger_pose_data)
    elif socket_data_type == DataTypes.REQUEST_LEARNING_DATA:
        print('received learning request')
        # FIXME: ideally send data based on the request
    else:
        print(f'Unsupported data type: {socket_data_type}')


def _handle_finger_pose(finger_pose_data):
    global _finger_pose_buffer

    # see whether the pose if pointing to an object for a certain duration based on history
    if len(_finger_pose_buffer) >= LearningConfig.finger_pointing_buffer_size:
        prev_avg_camera_x = statistics.mean([_data.camera_x for _data in _finger_pose_buffer])
        prev_avg_camera_y = statistics.mean([_data.camera_y for _data in _finger_pose_buffer])

        print(f'Current:: x: {finger_pose_data.camera_x}, y: {finger_pose_data.camera_y}, '
              f'Previous (avg):: x: {prev_avg_camera_x}, y: {prev_avg_camera_y}')

        # remove the oldest data
        _finger_pose_buffer.pop(0)

        # if same location, identify object data and send it to the client
        if same_pointing_location(prev_avg_camera_x, prev_avg_camera_y, finger_pose_data,
                                  LearningConfig.finger_pointing_location_offset):
            object_of_interest = _get_detected_object(finger_pose_data)
            if object_of_interest is not None:
                _send_learning_data(object_of_interest)

    # temporary store finger pose data
    _finger_pose_buffer.append(finger_pose_data)


def _send_learning_data(object_of_interest):
    learning_content = get_learning_data(object_of_interest)
    learning_data_handler.send_learning_data(object_of_interest, learning_content)


def same_pointing_location(camera_x, camera_y, finger_pose_data, offset):
    finger_x = finger_pose_data.camera_x
    finger_y = finger_pose_data.camera_y

    return abs(camera_x - finger_x) < offset and abs(camera_y - finger_y) < offset


def _get_detected_object(finger_pose_data):
    global _image_detector

    if _image_detector is None:
        return None

    # get the object of interest
    _, frame_width, frame_height, _ = _image_detector.get_source_params()
    image_region = get_image_region(finger_pose_data.camera_x, finger_pose_data.camera_y,
                                    frame_width, frame_height,
                                    LearningConfig.finger_pointing_location_offset)

    detections = _image_detector.get_last_detection()
    # FIXME: check detection time and not null
    detections = _image_detector.get_detection_in_region(detections, image_region)
    class_labels = _image_detector.get_class_labels()
    objects = [class_labels[class_id] for _, _, _, class_id, _ in detections]
    objects = [s for s in set(objects) if s != 'person']
    print(f'Objects[{len(objects)}]: {objects}')

    if len(objects) > 0:
        return objects[0]
    return None


def get_image_region(relative_x, relative_y, actual_width, actual_height, offset_length):
    image_x = int(relative_x * actual_width)
    image_y = int(relative_y * actual_height)
    image_offset = int(offset_length * actual_width / 2)
    image_region = [image_x - image_offset,
                    image_y - image_offset,
                    image_x + image_offset,
                    image_y + image_offset]
    return image_region


def configure_learning(image_detector):
    global _image_detector

    _image_detector = image_detector


def update_learning(finger_pointing_data = None):
    _handle_learning_requests(finger_pointing_data)
