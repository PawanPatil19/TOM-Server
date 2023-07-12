import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import sys
import numpy as np
import os, json, cv2, random
import mss
import tqdm
import warnings
import time
import tempfile
import multiprocessing as mp
import argparse
import glob

from ObjectDetectionCounter import ObjectDetectionCounter
from VideoStream import VideoStream

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog

# Detic libraries
sys.path.insert(0, './modules/Detic/third_party/CenterNet2/')
from centernet.config import add_centernet_config
from modules.Detic.detic.config import add_detic_config
from modules.Detic.detic.modeling.utils import reset_cls_test
from modules.Detic.detic.predictor import VisualizationDemo

WINDOW_NAME = "Detic"

class ScreenGrab:
    def __init__(self):
        self.sct = mss.mss()
        m0 = self.sct.monitors[0]
        self.monitor = {'top': 0, 'left': 0, 'width': m0['width'] / 2, 'height': m0['height'] / 2}

    def read(self):
        img =  np.array(self.sct.grab(self.monitor))
        nf = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return (True, nf)

    def isOpened(self):
        return True
    def release(self):
        return True
    
class VideoDetection:
    def __init__(
        self,
        video_path=0,
        save=False,
        save_path="detic_video_output.avi",
        object_counter_duration = 1
    ):
        self.videoPath = video_path
        self.useWebcam = False
        self.useStream = False
        self.captureInProgress = False
        self.capture = None
        self.stream = None
        self.last_detection = None
        self.save = save
        self.savePath = save_path
        self.inputType = 0
        
        
        if object_counter_duration > 0:
            self.object_detection_counter = ObjectDetectionCounter(object_counter_duration)
        else:
            self.object_detection_counter = None
        
        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path       : " + str(self.videoPath))
        

        # Build the detector and download our pretrained weights
        self.cfg = get_cfg()
        add_centernet_config(self.cfg)
        add_detic_config(self.cfg)
        self.cfg.MODEL.DEVICE="cpu"
        self.cfg.merge_from_file("./modules/Detic/configs/Detic_LCOCOI21k_CLIP_R18_640b32_4x_ft4x_max-size.yaml")
        self.cfg.MODEL.WEIGHTS = 'https://dl.fbaipublicfiles.com/detic/Detic_LCOCOI21k_CLIP_R18_640b32_4x_ft4x_max-size.pth'
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
        self.cfg.MODEL.ROI_BOX_HEAD.ZEROSHOT_WEIGHT_PATH = 'rand'
        self.cfg.MODEL.ROI_HEADS.ONE_CLASS_PER_PROPOSAL = True # For better visualization purpose. Set to False for all classes.
        # cfg.MODEL.DEVICE='cpu' # uncomment this to use cpu-only mode.
        #predictor = DefaultPredictor(cfg)

        # Setup the model's vocabulary using build-in datasets


        
    def __IsCaptureDev(self, videoPath):
        try:
            return '/dev/video' in videoPath.lower()
        except (ValueError, AttributeError):
            return videoPath == 0

    def __IsRtsp(self, videoPath):
        try:
            if 'rtsp:' in videoPath.lower() or '/api/holographic/stream' in videoPath.lower():  # or '0' in videoPath:
                return True
        except (ValueError, AttributeError):
            return False

    def __enter__(self):
        self.set_video_source(self.videoPath)
        return self


    def get_detect_object_percentage(self):
        if self.object_detection_counter:
            return  self.object_detection_counter.get_detected_object_percentage()

        return None

    def set_video_source(self, new_video_path):
        print("Video Path: " + str(new_video_path))

        if self.captureInProgress:
            self.captureInProgress = False

        if self.capture:
            self.capture.release()
            self.capture = None
        elif self.stream:
            self.stream.stop()
            self.stream = None

        self.videoPath = new_video_path
        self.useWebcam = self.__IsCaptureDev(new_video_path)
        self.useStream = self.__IsRtsp(new_video_path)

        if self.useWebcam:
            print("   - Using webcam")
            self.inputType = "0"
            self.capture = cv2.VideoCapture(new_video_path)
            if self.capture.isOpened():
                self.captureInProgress = True
        elif self.useStream:
            print("   - Using stream")
            self.inputType = "1"
            self.stream = VideoStream(new_video_path).start()
            time.sleep(1.0) # wait until loading at least one frame
            self.captureInProgress = True
        else:
            print("   - Using video file")

        if not self.captureInProgress:
            print("\nWARNING : Failed to Open Video Source\n")

    def start(self):
        while True:
            if self.captureInProgress:
                self.__Run__()

            if not self.captureInProgress:
                time.sleep(1.0)



    def __Run__(self):
        print("VideoCapture::__Run__()")
        mp.set_start_method("spawn", force=True)
        args =  argparse.Namespace(
            config_file="configs/Detic_LCOCOI21k_CLIP_R18_640b32_4x_ft4x_max-size.yaml",
            webcam=self.inputType,
            vocabulary="lvis",
            input=None,
            output=None
        )
        
        setup_logger(name="fvcore")
        logger = setup_logger()
        
        logger.info("Arguments: " + str(args))
        demo = VisualizationDemo(self.cfg, args)
        
        # cfg = setup_cfg(args)
        
        detection_results = []

        
        if self.useWebcam or self.useStream :
            print("   - Using webcam")
            
            assert args.input is None, "Cannot have both --input and --webcam!"
            assert args.output is None, "output not yet supported with --webcam!"
            if args.webcam == "screen":
                cam = ScreenGrab()
            elif args.webcam == "0":
                cam = cv2.VideoCapture(int(args.webcam))
            else :
                cam = self.stream
                
            for vis, predictions, confidence, bounding_boxes in tqdm.tqdm(demo.run_on_video(cam)):
                
                # get the predictions in the required format
                for i in range(len(predictions)):
                    tmp = [predictions[i], confidence[i], bounding_boxes[i]]
                
                
                detection_results.append(tmp)
                if self.object_detection_counter:
                    self.object_detection_counter.infer_counting(detection_results)

                self.last_detection = detection_results
                
                
                cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
                cv2.imshow(WINDOW_NAME, vis)
                if cv2.waitKey(1) == 27:
                    break  # esc to quit
            cam.release()
            cv2.destroyAllWindows()
    
    
    def get_last_detection(self):
        return self.last_detection

    def __exit__(self, exception_type, exception_value, traceback):

        if self.capture:
            self.capture.release()

        if self.stream:
            self.stream.stop()

        cv2.destroyAllWindows()
        
            