# wrapper for https://github.com/orcasgit/python-fitbit 


from . import gather_keys_oauth2 as Oauth2
import fitbit
import pandas as pd
import datetime
import json

# from .. utilities import  file as file_utility
import utilities.file as file_utility

# DO NOT CHANGE FOLLOWING
DATA_TYPE_HEART_RATE = 'activities/heart'
DATA_TYPE_STEPS = 'activities/steps'
DATA_TYPE_DISTANCE = 'activities/distance'
DATA_TYPE_ELEVATION = 'activities/elevation'
DATA_TYPE_CALORIES = 'activities/calories'
# DATA_TYPE_SPO2 = 'spo2'
# DATA_TYPE_BREATHING_RATE = 'br' 
 
DETAIL_LEVEL_1SEC = '1sec'
DETAIL_LEVEL_1MIN = '1min'
DETAIL_LEVEL_5MIN = '5min'
DETAIL_LEVEL_15MIN = '15min'

FITBIT_CREDENTIAL_FILE = 'credential/fitbit_credential.json'  # has the 'client_id' and 'client_secret'
KEY_CLIENT_ID = 'client_id'
KEY_CLIENT_SECRET = 'client_secret'

FITBIT_TOKEN_FILE = 'credential/fitbit_token.json'  # has the 'access_token' and 'refresh_token'
KEY_ACCESS_TOKEN = 'access_token'
KEY_REFRESH_TOKEN = 'refresh_token'

FITBIT_TOKEN_TOKEN_AGE_SECONDS = 8 * 60 * 60  # how long the token is valid for 8 hours

TODAY = str(datetime.datetime.now().strftime("%Y-%m-%d"))  # 'yyyy-MM-dd'


# return {'client_id': XX, 'client_secret': XX}
def read_fitbit_credential():
    print('Reading Fitbit credentials')
    with open(FITBIT_CREDENTIAL_FILE, 'r') as f:
        credential = json.load(f)
    return credential


def read_fitbit_token():
    print('Reading Fitbit token')

    if not file_utility.is_file_exists(FITBIT_TOKEN_FILE):
        return None

    if file_utility.is_file_older_than(FITBIT_TOKEN_FILE, FITBIT_TOKEN_TOKEN_AGE_SECONDS):
        return None

    with open(FITBIT_TOKEN_FILE, 'r') as f:
        credential = json.load(f)
    return credential


def save_fitbit_token(token):
    try:
        with open(FITBIT_TOKEN_FILE, 'w') as outfile:
            json.dump(token, outfile)
    except Exception as e:
        print(f'Failed to save order data: {FITBIT_TOKEN_FILE}, {e.__class__}')


# return {'access_token': XX, 'refresh_token': XX}
def get_authorize_token(credential):
    server = Oauth2.OAuth2Server(credential[KEY_CLIENT_ID], credential[KEY_CLIENT_SECRET])
    server.browser_authorize()
    return {KEY_ACCESS_TOKEN: str(server.fitbit.client.session.token['access_token']),
            KEY_REFRESH_TOKEN: str(server.fitbit.client.session.token['refresh_token'])}


def get_auth_client(credential, token):
    return fitbit.Fitbit(credential[KEY_CLIENT_ID], credential[KEY_CLIENT_SECRET], oauth2=True,
                         access_token=token[KEY_ACCESS_TOKEN],
                         refresh_token=token[KEY_REFRESH_TOKEN])


# see https://dev.fitbit.com/build/reference/web-api/intraday/get-activity-intraday-by-interval/ for data format
# date = <yyyy-MM-dd>, type = <DATA_TYPE_...>, detail_level = <DETAIL_LEVEL_...>, time = <HH:mm>,
def get_json_data(auth_client, date, type, detail_level, start_time=None, end_time=None):
    return auth_client.intraday_time_series(type, base_date=date, detail_level=detail_level,
                                            start_time=start_time, end_time=end_time)


# "activities-steps": [
#     {
#         "dateTime": "2019-01-01",
#         "value": "0"
#     }
# ],
# return 'date' (YYYY-MM-DD), 'count'
def get_date_and_count(json_data, type):
    type_key = type.replace("/", "-")
    data = json_data[type_key]
    return data['dateTime'], data['value']


# "activities-steps-intraday": {
#     "dataset": [
#         {
#             "time": "08:00:00",
#             "value": 0
#         },
#         {
#             "time": "08:01:00",
#             "value": 0
#         },
#         {
#             "time": "08:02:00",
#             "value": 0
#         },
# return data_frame with 'time' and 'value'
def get_data_frame(json_data, type):
    type_key = type.replace("/", "-") + "-intraday"
    return pd.DataFrame(json_data[type_key]['dataset'])


