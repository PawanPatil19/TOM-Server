# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import sys

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
    main(
        0,
        True,
        0.7,
        [],
        True,
        True,
        True,
        'yolo_video_output.avi',
        1,
        )

if __name__ == '__main__':
    Run()