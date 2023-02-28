# coding=utf-8

HOLOLENS_IP = "192.168.5.21"
DEVICE_PORTAL_USERNAME = "hellojanaka"
DEVICE_PORTAL_PASSWORD = "testing1234"

DEVICE_STREAM_SETTINGS = "holo=true&pv=true&mic=false&loopback=true"

def get_ip():
    return HOLOLENS_IP


def get_username():
    return DEVICE_PORTAL_USERNAME


def get_password():
    return DEVICE_PORTAL_PASSWORD


def get_stream_setting():
    return DEVICE_STREAM_SETTINGS