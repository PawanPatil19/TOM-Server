# coding=utf-8

import pytest

import modules.utilities.time as time_utility

def test_get_date_string():
    assert time_utility.get_date_string() == "20230221"