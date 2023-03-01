# coding=utf-8

import modules.utilities.network as network_utility
from . import hololens_config as hololens_config

# Note: Need to disable SSL connection (System->Preference)

CREDENTIALS = {
    'username': hololens_config.get_username(),
    'password': hololens_config.get_password()
}

# Ref: 
#	- https://docs.microsoft.com/en-us/windows/mixed-reality/develop/advanced-concepts/device-portal-api-reference
#	- https://docs.microsoft.com/en-us/windows/uwp/debug-test-perf/device-portal-api-core
API_BASE = f'https://{hololens_config.get_ip()}/api'
API_START_RECORDING = f'{API_BASE}/holographic/mrc/video/control/start?holo=true&pv=true&mic=true&loopback=true&RenderFromCamera=true'  # POST 
API_STOP_RECORDING = f'{API_BASE}/holographic/mrc/video/control/stop'  # POST
API_GET_RECORDINGS = f'{API_BASE}/holographic/mrc/files'  # GET
API_GET_RECORDING_STATUS = f'{API_BASE}/holographic/mrc/status'  # GET
API_TAKE_PHOTO = f'{API_BASE}/holographic/mrc/photo?holo=true&pv=true'  # POST

API_STREAM_VIDEO = f'https://{hololens_config.get_username()}:{hololens_config.get_password()}@{hololens_config.get_ip()}/api/holographic/stream/live_med.mp4?{hololens_config.get_stream_setting()}'

# return True if success else False
def start_recording():
    return network_utility.send_post_request(API_START_RECORDING, "", CREDENTIALS)


# return True if success else False
def stop_recording():
    return network_utility.send_post_request(API_STOP_RECORDING, "", CREDENTIALS)


def take_photo():
    return network_utility.send_post_request(API_TAKE_PHOTO, "", CREDENTIALS)


# return list of files ([{'CreationTime': xx, 'FileName': 'xx.mp4', 'FileSize': xx}])
def get_saved_recordings():
    res = network_utility.send_get_request(API_GET_RECORDINGS, CREDENTIALS)
    if res is None or not res:
        return []

    return res['MrcRecordings']


# return True if recording
def get_recording_status():
    res = network_utility.send_get_request(API_GET_RECORDING_STATUS, CREDENTIALS)
    if res is None:
        return False

    return res['IsRecording']

# print(get_saved_recordings())
# start_recording()
# utilities.sleep_seconds(3)
# print(get_recording_status())
# utilities.sleep_seconds(3)
# stop_recording()
# utilities.sleep_seconds(1)
# print(get_recording_status())
# take_photo()
# print(get_saved_recordings())
