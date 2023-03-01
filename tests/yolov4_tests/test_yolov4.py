# coding=utf-8

import pytest
import sys

import modules.yolov4.VideoCapture as YoloDetector

def test_yolo():
    try:
        with YoloDetector(0) as yoloDetector:
            yoloDetector.start()
    except KeyboardInterrupt:
        print("Yolo module stopped" )
        