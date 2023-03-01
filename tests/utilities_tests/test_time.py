# coding=utf-8

import pytest

import modules.utilities.time as time_utility

def test_get_date():
    assert time_utility.get_date() == "20230221"