import modules.fitbit_web.web_api as fitbit_web_api
import modules.utilities.time as time_utility
import modules.websocket_server.socket_server as socket_server



flag_is_running = False

def start_app():
    global flag_is_running

    if flag_is_running:
        print('Another instance is running')
        return

    flag_is_running = True

    fitbit_credential = fitbit_web_api.read_fitbit_credential()
    fitbit_token = fitbit_web_api.read_fitbit_token()
    if fitbit_token is None:
        fitbit_token = fitbit_web_api.get_authorize_token(fitbit_credential)
        fitbit_web_api.save_fitbit_token(fitbit_token)

    fitbit_client = fitbit_web_api.get_auth_client(fitbit_credential, fitbit_token)
    today_string = time_utility.get_date("%Y-%m-%d")
    print(today_string)

    # fitbit_raw_data_distance = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_DISTANCE, fitbit_web_api.DETAIL_LEVEL_1MIN)
    # print(f'\ndistance: {fitbit_raw_data_distance}')
    # 
    # fitbit_raw_data_steps = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_STEPS, fitbit_web_api.DETAIL_LEVEL_1MIN)
    # print(f'\nsteps: {fitbit_raw_data_steps}')

    socket_server.start_server_threaded()
    current_millis = 0

    while flag_is_running:
        if time_utility.get_current_millis() - current_millis > 10*1000:

            fitbit_raw_data_heart_rate = fitbit_web_api.get_json_data(fitbit_client, today_string, fitbit_web_api.DATA_TYPE_HEART_RATE, fitbit_web_api.DETAIL_LEVEL_1SEC)
            # print(fitbit_raw_data_heart_rate)
            df = fitbit_web_api.get_data_frame(fitbit_raw_data_heart_rate, fitbit_web_api.DATA_TYPE_HEART_RATE)
            df_last_row = df.iloc[-1] # time, value
            last_row_val = df_last_row['value']
            # last_row_val = 100

            socket_server.send_data(f'HR: {last_row_val}')

            # utilities.send_get_request(f'http://127.0.0.1:5050/?HR: {last_row_val}=1')
            # curl -X POST -d "" http://127.0.0.1:5050/?Hello=1 

            current_millis = time_utility.get_current_millis()


        time_utility.sleep_seconds(1)

    socket_server.stop_server_threaded()


start_app()
