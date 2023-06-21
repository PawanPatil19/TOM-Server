# coding=utf-8

import sys
import time
from datetime import datetime
from datetime import timedelta


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


def get_date_string(format="%Y%m%d"):
    return time.strftime(format)


def get_time_string(format="%H:%M:%S"):
    return time.strftime(format)


# return date_time object
def get_date_time_now():
    return datetime.now()


def get_date_time_diff_string(date_time1, date_time2, format="%H:%M:%S"):
    return (date_time1 - date_time2).strftime("%H:%M:%S")


def get_hh_mm_ss_format(seconds):
    result = str(timedelta(seconds=seconds))  # format=<0:00:10.10000>
    return result.lstrip('0').lstrip(':')

# print(get_date())
# print(get_date("%Y-%m-%d"))
# print(get_hh_mm_ss_format(10))
# print(get_hh_mm_ss_format(65))
# print(get_hh_mm_ss_format(3665.1))
