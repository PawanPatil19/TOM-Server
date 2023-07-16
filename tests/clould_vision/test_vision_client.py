# coding=utf-8

import pytest

from modules.cloud_vision.VisionClient import VisionClient as TextDetector

def test_text_detection():
    text_detector = TextDetector()
    res = text_detector.detect_text_image_uri("gs://cloud-samples-data/vision/ocr/sign.jpg")

    assert res == ""


