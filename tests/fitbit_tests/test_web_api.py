
import pytest

import modules.utilities.time as time_utility
import modules.fitbit_web.web_api as fitbit_web_api


def test_api():
    fitbit_credential = fitbit_web_api.read_fitbit_credential()
    fitbit_token = fitbit_web_api.read_fitbit_token()
    if fitbit_token is None:
        fitbit_token = fitbit_web_api.get_authorize_token(fitbit_credential)
        fitbit_web_api.save_fitbit_token(fitbit_token)

    fitbit_client = fitbit_web_api.get_auth_client(fitbit_credential, fitbit_token)
    today_string = time_utility.get_date_string("%Y-%m-%d")

    fitbit_raw_data_distance = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_DISTANCE, fitbit_web_api.DETAIL_LEVEL_1MIN)
    # print(f'\ndistance: {fitbit_raw_data_distance}')

    fitbit_raw_data_steps = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_STEPS, fitbit_web_api.DETAIL_LEVEL_1MIN)
    # print(f'\nsteps: {fitbit_raw_data_steps}')

    fitbit_raw_data_heart_rate = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_HEART_RATE, fitbit_web_api.DETAIL_LEVEL_1SEC)
    # print(f'\nheart rate: {fitbit_raw_data_heart_rate}')

    df = fitbit_web_api.get_data_frame(fitbit_raw_data_heart_rate, fitbit_web_api.DATA_TYPE_HEART_RATE)
    df_last_row = df.iloc[-1] # time, value
    last_row_val = df_last_row['value']

    assert last_row_val == '70'
