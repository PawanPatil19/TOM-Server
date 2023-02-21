# coding=utf-8

import sys
import time
import re


def get_int(string_value):
    return int(string_value)


def get_float(string_value):
    return float(string_value)


def is_empty(string_value):
    return string_value is None or string_value == ""


def get_text_without_parentheses_text(text):
    return re.sub("[\(\[].*?[\)\]]", "", text)


def get_text_inside_parentheses(text):
    # return re.findall('\(.*?\)', text)
    return re.findall('[\(\[].*?[\)\]]', text)


def get_first_text_inside_parentheses_without_parentheses(text):
    # return re.findall('\(.*?\)', text)
    return re.findall('[\(\[].*?[\)\]]', text)[0].replace("[", "").replace("]", "")


# print(get_text_without_parentheses_text("[hi]"))
# print(get_text_inside_parentheses("[hi]"))
# print(get_first_text_inside_parentheses_without_parentheses("[hi]"))
# print(get_text_inside_parentheses("[]"))
# print(get_first_text_inside_parentheses_without_parentheses("[]"))
# print(get_text_inside_parentheses(""))


