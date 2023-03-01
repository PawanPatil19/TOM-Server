#To make python 2 and python 3 compatible code
from __future__ import division
from __future__ import absolute_import

import sys
import cv2
import numpy as np
import time


from VideoStream import VideoStream
from StatusHandler import StatusHandler

#import YoloInference
#from YoloInference import YoloInference

from detector.detector import Detector

class VideoCapture:

    def __init__(
            self,
            video_path = 0, # if webcam 0, else source
            inference = True, # if object recognition is needed
            confidence_level = 0.7, # the minimum confidence level to say it is a valid detection
            custom_classes = [], # list of custom classe, else default YOLO classes
            tiny = True, # if model is YOLO, delect if tiny version should be used which achieves around 30 frames per second on CPU
            show = True, # show (live) the detections in a video by drawing rectangle boxes and assigning confidence values
            save = True, # save the detections in a video by drawing rectangle boxes and assigning confidence values
            save_path = 'yolo_video_output.avi', # video saving path
            min_time = 1, # minimum time in seconds a thing must be in the screen so that we display any recommendations
            ):

        self.videoPath = video_path
        self.inference = inference
        self.confidenceLevel = confidence_level
        self.useStream = False
        self.useWebcam = False
        self.useMovieFile = False
        self.frameCount = 0
        self.vStream = None
        self.vCapture = None
        self.displayFrame = None
        self.captureInProgress = False
        self.customClasses = custom_classes
        self.tiny = tiny
        self.showResult = show
        self.saveResult = save
        self.resultPath = save_path
        self.recommendation_thresh = min_time
        
        self.custom = len(self.customClasses) > 0
        self.detections_queue = []
        

        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path       : " + str(self.videoPath))
        print("   - Inference?       : " + str(self.inference))
        print("   - ConfidenceLevel  : " + str(self.confidenceLevel))
        print("   - CustomDetection? : " + str(self.custom))
        if self.custom:
            print("   - Custom Classes   : " + str(self.customClasses))
        
        self.yoloInference = Detector(tiny=self.tiny, custom=self.custom) # yolov4

        if self.custom:
            self.statusHandler = StatusHandler(self.customClasses)
        else:
            self.statusHandler = StatusHandler()

    def __IsCaptureDev(self, videoPath):
        try: 
            return '/dev/video' in videoPath.lower()
        except (ValueError, AttributeError):
            return videoPath == 0

    def __IsRtsp(self, videoPath):
        try:
            if 'rtsp:' in videoPath.lower() or '/api/holographic/stream' in videoPath.lower(): #or '0' in videoPath:
                return True
        except ValueError:
            return False

    def __enter__(self):

        self.setVideoSource(self.videoPath)

        return self

    def setVideoSource(self, newVideoPath):

        if self.captureInProgress:
            self.captureInProgress = False
            time.sleep(1.0)
            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None
            elif self.vStream:
                self.vStream.stop()
                self.vStream = None

        if self.__IsRtsp(str(newVideoPath)):
            print("\r\n===> RTSP Video Source")

            self.useStream = True
            self.useMovieFile = False
            self.useWebcam = False
            self.videoPath = newVideoPath

            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.vStream = VideoStream(newVideoPath).start()
            # Needed to load at least one frame into the VideoStream class
            time.sleep(1.0)
            self.captureInProgress = True

        elif self.__IsCaptureDev(newVideoPath):
            print("===> Webcam Video Source")
            if self.vStream:
                self.vStream.start()
                self.vStream = None

            if self.vCapture:
                self.vCapture.release()
                self.vCapture = None

            self.videoPath = newVideoPath
            self.useMovieFile = False
            self.useStream = False
            self.useWebcam = True
            self.vCapture = cv2.VideoCapture(newVideoPath)
            if self.vCapture.isOpened():
                self.captureInProgress = True
            else:
                print("===========================\r\nWARNING : Failed to Open Video Source\r\n===========================\r\n")
        else:
            print("===========================\r\nWARNING : No Video Source\r\n===========================\r\n")
            self.useStream = False
            self.useWebcam = False
            self.vCapture = None
            self.vStream = None
        return self

    def get_display_frame(self):
        return self.displayFrame

    def videoStreamReadTimeoutHandler(signum, frame):
        raise Exception("VideoStream Read Timeout") 

    def start(self):
        while True:
            if self.captureInProgress:
                self.__Run__()

            if not self.captureInProgress:
                time.sleep(1.0)

    def get_detected_objects(self):
        return self.detections_queue.copy()

    def __Run__(self):

        print("===============================================================")
        print("videoCapture::__Run__()")
        print("   - Stream          : " + str(self.useStream))
        print("   - useMovieFile    : " + str(self.useMovieFile))
        print("   - useWebcam       : " + str(self.useWebcam))

        '''
        # check if stream is opened
        if self.useStream:
            print("Stream is opnened {}".format(self.vStream.stream.isOpened()))
        elif self.useWebcam:
            print("Stream is opnened {}".format(self.vCapture.isOpened()))
        '''

        # Check camera's FPS
        if self.useStream:
            cameraFPS = int(self.vStream.stream.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.vStream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        elif self.useWebcam:
            cameraFPS = int(self.vCapture.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.vCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.vCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if cameraFPS == 0:
            print("Error : Could not get FPS")
            raise Exception("Unable to acquire FPS for Video Source")
            return

        print("Frame rate (FPS)     : " + str(cameraFPS))

        currentFPS = cameraFPS
        perFrameTimeInMs = 1000 / cameraFPS

        # by default VideoCapture returns float instead of int
        if self.saveResult: 
            codec = cv2.VideoWriter_fourcc(*"XVID")
            frame_size = (frame_width, frame_height)
            out = cv2.VideoWriter(self.resultPath, codec, cameraFPS, frame_size)
        
        if self.showResult:
            cv2.namedWindow("Camera")
            cv2.moveWindow("Camera", 0, 0)

        index_boundary = None        
        last_fps = 0

        while True:
            tFrameStart = time.time()

            if not self.captureInProgress:
                break
            try:
                if self.useStream:
                    frame = self.vStream.read()
                    
                else:
                    frame = self.vCapture.read()[1]
                    
            except Exception as e:
                print("ERROR : Exception during capturing")
                raise(e)

            # Run Object Detection
            if self.inference:
                detections, image = self.yoloInference.detect(frame)

                fps = 1.0 / (time.time() - tFrameStart)

                # update index boundary if FPS rate has changed significantly, tests have shown that all equal or below 0.3 is not significant
                if (fps - last_fps) > 0.3:
                    # how many elements back in the queue we have to scan for an object
                    # index_boundary is the index position of the frame that was processed MIN_SECONDS ago
                    index_boundary = int(round(fps / (1/self.recommendation_thresh), 0))
            
                print("FPS: %.2f" % fps)

                last_fps = fps

                if self.showResult or self.saveResult:
                    result = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    if self.saveResult:
                        out.write(result)
                        
                    if self.showResult:
                        cv2.imshow("Camera", result)
                        if cv2.waitKey(10) & 0xFF == ord('q'):
                            break
                
                # handle Object presence
                if len(detections) > 0:
                    queue_list = []
                    for detection in detections:
                        classLabel, confidence = detection[0], detection[1]
                        if confidence > self.confidenceLevel:
                            
                            # as we don't care about the color because we retrieve the current air quality from the sensor directly and not over the color of the hue lamp
                            if "hue" in classLabel:
                                classLabel = "hue"

                            queue_list.append(classLabel)
                            
                            print("Object: {}".format(classLabel))
                            print("Confidence: {}".format(confidence))

                            # if notification should be send out to endpoint that thing is present
                            try:
                                # we only send the notification once, when the state changes from 0 to 1
                                if self.statusHandler.statuses[classLabel] != 1:

                                    ThingIsThere = True

                                    # if queue is already long enough, will equal to False for the first few frames
                                    if len(self.detections_queue) >= index_boundary:
                                        # iterate over each previous detection
                                        for i in self.detections_queue:
                                            # check if thing has been detected in each previous frame of the queue
                                            if any(classLabel in sl for sl in i):
                                                continue
                                            else:
                                                # thing is relatively new / user is not looking long enough at the thing
                                                ThingIsThere = False
                                                break
                                    else:
                                        # thing is there and notification has already been sent
                                        ThingIsThere = False

                                    if ThingIsThere:
                                        print("Thing {} is present.".format(classLabel))
                                        # TODO: send call to display all actions on the Hololens that are related with this object
                                        # if self.statusHandler.statuses[classLabel] != 1:
                                            

                                # when thing is not of interest to us
                            except KeyError:
                                pass
                                

                # build the new queue element
                try:
                    if len(queue_list) > 0:
                        # made some detections
                        self.detections_queue.append(queue_list)
                        queue_list = []
                    else:
                        # confidence too low or no detections at all
                        self.detections_queue.append(["NaN"])
                except NameError:
                    # no detections at all
                    self.detections_queue.append(["NaN"])
                         
                # calculate new first element of queue
                first_element = len(self.detections_queue) - index_boundary
                if first_element > 0:
                    # update queue, leave out elements that are longer than MIN_TIME seconds ago
                    self.detections_queue = self.detections_queue[first_element:]

                print(self.detections_queue)

                # get list of all objects that are currently there
                things_displayed = [thing for thing, pres in self.statusHandler.statuses.items() if pres == 1]

                # check if all object are still there
                for thing in things_displayed: 
                    # check if thing is still somewhere in the queue
                    ThingIsThere = False
                    for i in self.detections_queue:
                        if any(thing in sl for sl in i):
                            ThingIsThere = True
                            break
                    
                    # thing is no longer in queue
                    if not ThingIsThere:
                        print("Thing {} is not present anymore.".format(thing))
                        # TODO: update state
                        # if self.statusHandler.statuses[thing] != 0:
                
            # Calculate FPS rate at which the VideoCapture is able to process the frames
            timeElapsedInMs = (time.time() - tFrameStart) * 1000
            currentFPS = 1000.0 / timeElapsedInMs

            if (currentFPS > cameraFPS):
                # Cannot go faster than Camera's FPS
                currentFPS = cameraFPS

            timeElapsedInMs = (time.time() - tFrameStart) * 1000

            if (1000 / cameraFPS) > timeElapsedInMs:
                # This is faster than image source (e.g. camera) can feed.  
                waitTimeBetweenFrames = perFrameTimeInMs - timeElapsedInMs
                time.sleep(waitTimeBetweenFrames/1000.0)

    def __exit__(self, exception_type, exception_value, traceback):

        if self.vCapture:
            self.vCapture.release()

        # self.imageServer.close()
        cv2.destroyAllWindows()