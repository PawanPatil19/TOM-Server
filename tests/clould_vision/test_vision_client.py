# coding=utf-8

import pytest
import cv2

from modules.cloud_vision.VisionClient import VisionClient as TextDetector


def test_detect_text_image_uri():
    text_detector = TextDetector()
    res = text_detector.detect_text_image_uri("gs://cloud-samples-data/vision/ocr/sign.jpg")

    assert res == ""


def test_detect_text_frame():
    cap = cv2.VideoCapture(
        0)  # 0 is the default camera. Replace with the file path for an image file.
    ret, frame = cap.read()

    text_detector = TextDetector()
    res = text_detector.detect_text_frame(frame)

    assert res == ""
