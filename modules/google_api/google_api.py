
import json


GOOGLE_CREDENTIAL_FILE = 'credential/google_credential.json'  # has the 'map_api_key', ...
KEY_MAP_API = 'map_api_key'


# return {"map_api_key": "YYY"}
def read_google_credential():
    print('Reading Google credentials')
    with open(GOOGLE_CREDENTIAL_FILE, 'r') as f:
        credential = json.load(f)
    return credential


def get_google_credential(key, credential = None):
    _credential = credential
    if _credential is None:
        _credential = read_google_credential()

    return _credential[key]
