# coding=utf-8
import json
import modules.utilities.network as network_utility
from config import HOLOLENS_CREDENTIAL_FILE

# Note: Need to disable SSL connection (System->Preference)

DEVICE_STREAM_SETTINGS = "holo=true&pv=true&mic=false&loopback=true"

def read_hololens_credential():
    print('Reading HoloLens credentials')
    with open(HOLOLENS_CREDENTIAL_FILE, 'r') as f:
        credential = json.load(f)
    return credential


CREDENTIALS = read_hololens_credential()
HOLOLENS_IP = CREDENTIALS['ip']
DEVICE_PORTAL_USERNAME = CREDENTIALS['username']
DEVICE_PORTAL_PASSWORD = CREDENTIALS['password']

print(f'HOLOLENS_IP: {HOLOLENS_IP}')

# Ref: 
#	- https://docs.microsoft.com/en-us/windows/mixed-reality/develop/advanced-concepts/device-portal-api-reference
#	- https://docs.microsoft.com/en-us/windows/uwp/debug-test-perf/device-portal-api-core
API_BASE = f'https://{HOLOLENS_IP}/api'
API_START_RECORDING = f'{API_BASE}/holographic/mrc/video/control/start?holo=true&pv=true&mic=true&loopback=true&RenderFromCamera=true'  # POST 
API_STOP_RECORDING = f'{API_BASE}/holographic/mrc/video/control/stop'  # POST
API_GET_RECORDINGS = f'{API_BASE}/holographic/mrc/files'  # GET
API_GET_RECORDING_STATUS = f'{API_BASE}/holographic/mrc/status'  # GET
API_TAKE_PHOTO = f'{API_BASE}/holographic/mrc/photo?holo=true&pv=true'  # POST

API_STREAM_VIDEO = f'https://{DEVICE_PORTAL_USERNAME}:{DEVICE_PORTAL_PASSWORD}@{HOLOLENS_IP}/api/holographic/stream/live_med.mp4?{DEVICE_STREAM_SETTINGS}'

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
