# coding=utf-8

import sys
import json
import requests

REQUEST_TIMEOUT = 3  # 5 seconds


# return True if success else False
def send_post_request(url, data, credentials=None):
    print('POST Request: {}, {}'.format(url, data))

    try:
        if credentials is None:
            x = requests.post(url, data=str(data).encode('ascii', 'ignore'),
                              timeout=REQUEST_TIMEOUT, verify=False)
        else:
            x = requests.post(url, data=str(data).encode('ascii', 'ignore'),
                              timeout=REQUEST_TIMEOUT, verify=False,
                              auth=(credentials['username'], credentials['password']))
        #         print(x.request.url)
        #         print(x.request.body)
        #         print(x.request.headers)
        print("{}\n".format(x.status_code))
        return True
    except Exception as e:
        print('Failed POST request', e)
        return False


# return json objects if success else None
# ref: https://requests.readthedocs.io/en/latest/user/quickstart/
def send_get_request(url, credentials=None):
    print('GET Request: {}'.format(url))

    try:
        if credentials is None:
            x = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
        else:
            x = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False,
                             auth=(credentials['username'], credentials['password']))
        # print("{}: {}\n".format(x.status_code, x.text))
        print("{}\n".format(x.status_code))
        return x.json()
    except Exception as e:
        print('Failed GET request', e)
        return None
