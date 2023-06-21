import os

credential_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credential')

GOOGLE_CREDENTIAL_FILE = os.path.join(credential_path, 'google_credential.json')
ORS_CREDENTIAL_FILE = os.path.join(credential_path, 'ors_credential.json')
