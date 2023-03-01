# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import sys
import time
import json
import yaml

import VideoCapture
from VideoCapture import VideoCapture

def main(
        videoPath,
        inference,
        confidenceLevel,
        custom_classes,
        tiny,
        show,
        save,
        output,
        min_time,
        ):

    global videoCapture

    try:
        print("\nPython %s\n" % sys.version )
        print("Yolo Capture Module. Press Ctrl-C to exit." )

        with VideoCapture(videoPath,
                         inference,
                         confidenceLevel,
                         custom_classes,
                         tiny,
                         show,
                         save,
                         output,
                         min_time,
                         ) as videoCapture:
                         
            videoCapture.start()

    except KeyboardInterrupt:
        print("Camera capture module stopped" )

def Run():
    try:
        with open("config.yml", "r") as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        if cfg['USE_WEBCAM']:
            VIDEO_PATH = 0
        else:
            VIDEO_PATH = cfg['VIDEO_SOURCE']
        
    except ValueError as error:
        print(error )
        sys.exit(1)

    main(
        VIDEO_PATH,
        cfg['RUN_INFERENCE'],
        cfg['MIN_CONFIDENCE_LEVEL'],
        cfg['CUSTOM_CLASSES'],
        cfg['USE_YOLO-TINY'],
        cfg['SHOW_OUTPUT'],
        cfg['SAVE_OUTPUT'],
        cfg['RESULT_PATH'],
        cfg['MIN_TIME'],
        )

if __name__ == '__main__':
    Run()