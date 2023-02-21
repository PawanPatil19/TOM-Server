# coding=utf-8

import sys
import time
import os
import json

import glob
from pathlib import Path


def append_data(file_name, data):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    try:
        file = open(file_name, "a")
        file.write(data)
        file.close()
    except Exception as e:
        print("Failed to write: ", e.__class__)


def is_file_exists(file_name):
    return os.path.exists(file_name)


# return lines
def read_file(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    return lines


def write_data(file_name, lines):
    try:
        file = open(file_name, "w")
        file.writelines(lines)
        file.close()
    except Exception as e:
        print("Failed to write: ", e.__class__)


# extension: extension with . (e.g. .csv)
def read_file_names(directory, extension, prefix):
    all_files_with_extension = [file for file in glob.glob(f'{directory}/*{extension}')]
    all_files_with_extension.sort()
    # print(all_files_with_extension)
    return [file for file in all_files_with_extension if Path(file).stem.startswith(prefix)]


# save the order info as {"order": <list>, "index": <index>}
def save_order_data(file_name, list_data, current_index):
    try:
        with open(file_name, 'w') as outfile:
            data = {'order': list_data, 'index': current_index}
            json.dump(data, outfile)
    except Exception as e:
        print(f'Failed to save order data: {file_name}, {e.__class__}')


# return the <list>: order, <index>:index
def read_order_data(file_name, max_duration_minutes):
    if not os.path.exists(file_name):
        return None, None

    # if order data file is older than <max_duration_minutes> minutes ignore it
    if is_file_older_than(file_name, max_duration_minutes * 60):
        return None, None

    # read recent order data file
    try:
        with open(file_name) as json_file:
            data = json.load(json_file)
            return data['order'], data['index']
    except Exception as e:
        print(f'Failed to read order data: {file_name}, {e.__class__}')
        return None, None


def is_file_older_than(file_name, seconds):
    file_time = os.path.getmtime(file_name)
    return (time.time() - file_time) > seconds
