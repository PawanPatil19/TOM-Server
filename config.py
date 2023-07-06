import os

credential_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credential')

HOLOLENS_CREDENTIAL_FILE = os.path.join(credential_path, 'hololens_credential.json')
FITBIT_CREDENTIAL_FILE = os.path.join(credential_path, 'fitbit_credential.json')
GOOGLE_CREDENTIAL_FILE = os.path.join(credential_path, 'google_credential.json')
OPENAI_CREDENTIAL_FILE = os.path.join(credential_path, 'openai_credential.json')
ORS_CREDENTIAL_FILE = os.path.join(credential_path, 'ors_credential.json')
GEOAPIFY_CREDENTIAL_FILE = os.path.join(credential_path, 'geoapify_credential.json')

# 0 for OSM, 1 for google maps
PLACES_OPTION = 1
# 0 for ORS, 1 for google maps
DIRECTIONS_OPTION = 1
# 0 for geoapify, 1 for google maps
STATIC_MAPS_OPTION = 1
# 0 for api key, 1 for localhost
ORS_OPTION = 0
