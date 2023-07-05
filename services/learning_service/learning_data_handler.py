import logging
import random

from google.protobuf.message import DecodeError

import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server

from modules.dataformat import socket_data_pb2
from modules.dataformat import request_data_pb2
from modules.dataformat import learning_data_pb2
from modules.dataformat import finger_pose_data_pb2
from modules.dataformat.data_types import DataTypes


def send_socket_server(data):
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()


def get_decoded_socket_data(socket_data):
    if socket_data is None or isinstance(socket_data, str):
        logging.error('Received data is not a valid socket_data instance: ' + socket_data)
        return None, None

    try:
        socket_data_msg = socket_data_pb2.SocketData()
        socket_data_msg.ParseFromString(socket_data)

        data_type = socket_data_msg.data_type
        data = socket_data_msg.data

        if data_type == DataTypes.FINGER_POINTING_DATA:
            return decode_finger_pose_data(data)
        elif is_request_data_type(data_type):
            return decode_request_data(data_type, data)
        else:
            logging.error('Unknown socket_data protobuf type')
            return data_type, None
    except DecodeError:
        logging.error('Received data is not a valid socket_data protobuf message')
        return None, None


# return <type, data>
def decode_finger_pose_data(data):
    try:
        finger_pose_data = finger_pose_data_pb2.FingerPoseData()
        finger_pose_data.ParseFromString(data)

        return DataTypes.FINGER_POINTING_DATA, finger_pose_data
    except DecodeError:
        logging.error('Received data is not a valid finger_pose_data protobuf message')
        return None, None


# return <type, data>
def decode_request_data(request_type, data):
    try:
        request_data = request_data_pb2.RequestData()
        request_data.ParseFromString(data)

        return request_type, request_data
    except DecodeError:
        logging.error('Received data is not a valid request_data protobuf message')
        return None, None


def is_request_data_type(data_type):
    return data_type in [
        DataTypes.REQUEST_LEARNING_DATA,
    ]


def send_learning_data(instruction="", detail="", speech=""):
    learning_data_proto = learning_data_pb2.LearningData(
        instruction=instruction,
        detail=detail,
        speech=speech,
    )
    learning_data_bytes = wrap_message_with_metadata(learning_data_proto, DataTypes.LEARNING_DATA)
    send_socket_server(learning_data_bytes)


def wrap_message_with_metadata(data, data_type):
    socket_data = socket_data_pb2.SocketData(
        data_type=data_type,
        data=data.SerializeToString()
    )

    return socket_data.SerializeToString()
