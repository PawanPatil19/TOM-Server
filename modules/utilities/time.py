# coding=utf-8

import sys
import time


def beep(times=1):
    for i in range(1, times):
        sys.stdout.write(f'\r\a{i}')
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write('\n')
    time.sleep(0.1)


def get_current_millis():
    return round(time.time() * 1000)


def sleep_seconds(seconds=0.2):
    count = 0
    delay_seconds = 0.05
    total_count = seconds * 19  # instead of 20

    while count < total_count:
        count += 1
        time.sleep(delay_seconds)


def sleep_milliseconds(milliseconds=1):
    time.sleep(milliseconds / 1000)


def get_date(format="%Y%m%d"):
    return time.strftime(format)

# print(get_date())
# print(get_date("%Y-%m-%d"))