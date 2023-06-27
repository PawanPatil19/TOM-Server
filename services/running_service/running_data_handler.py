
from google.protobuf.message import DecodeError


from modules.dataformat.data_types import DataTypes
from modules.dataformat import exercise_sensor_data_pb2
from modules.dataformat import socket_data_pb2
from modules.dataformat import running_data_pb2
from modules.dataformat import summary_data_pb2
from modules.dataformat import type_position_mapping_data_pb2

import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server


def send_socket_server(data):
    print(data)
    socket_server.send_data(data)


def get_socket_data():
    return socket_server.receive_data()


def get_exercise_sensor_data():
    socket_data = get_socket_data()
    if socket_data is None or isinstance(socket_data, str):
        return None

    try:
        exercise_sensor_data = exercise_sensor_data_pb2.ExerciseSensorData()
        exercise_sensor_data.ParseFromString(socket_data)
        return exercise_sensor_data
    except DecodeError:
        return None