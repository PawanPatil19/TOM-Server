import cv2
import supervision as sv
from ultralytics import YOLO
import time
import sys


class  VideoDetection:
    def __init__(
            self, 
            video_path = 0, 
            save_path = "yolo_video_output.avi",
            inference = True,
            model = "./modules/yolov8/weights/model.pt",
            save = False):
        self.videoPath = video_path
        self.savePath = save_path
        self.inference = inference
        self.model = model
        self.useWebcam = False
        self.useStream = False
        self.captureInProgress = False
        self.save = save
    
    
        print("VideoCapture::__init__()")
        print("OpenCV Version : %s" % (cv2.__version__))
        print("===============================================================")
        print("Initialising Video Capture with the following parameters: ")
        print("   - Video path       : " + str(self.videoPath))
        print("   - Inference?       : " + str(self.inference))
    
    def __IsCaptureDev(self, videoPath):
        try: 
            return '/dev/video' in videoPath.lower()
        except (ValueError, AttributeError):
            return videoPath == 0

    def __IsRtsp(self, videoPath):
        try:
            if 'rtsp:' in videoPath.lower() or '/api/holographic/stream' in videoPath.lower(): #or '0' in videoPath:
                return True
        except (ValueError, AttributeError):
            return False
        
        
    
    def __enter__(self):
        self.setVideoSource(self.videoPath)
        return self
    
    def setVideoSource(self, newVideoPath):
        self.videoPath = newVideoPath
        self.useWebcam = self.__IsCaptureDev(newVideoPath)
        self.useStream = self.__IsRtsp(newVideoPath)
        
        if self.useWebcam:
            print("   - Using webcam")
        elif self.useStream:
            print("   - Using stream")
        else:
            print("   - Using video file")
            
        self.capture = cv2.VideoCapture(self.videoPath)
        self.captureInProgress = True
        
    
    def start(self):
        while True:
            if self.captureInProgress:
                self.__Run__()
                
            if not self.captureInProgress:
                time.sleep(0.1)
            

    def __Run__(self):
        print("VideoCapture::__Run__()")
        # to save the video
        if self.save :
            writer= cv2.VideoWriter(self.savePath, 
                                    cv2.VideoWriter_fourcc(*'DIVX'), 
                                    7, 
                                    (1280, 720))
        
        print("Video Path: " + str(self.videoPath))
        # define resolution
        cap = cv2.VideoCapture(self.videoPath)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        # specify the model
        model = YOLO(self.model)

        # customize the bounding box
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )


        while True:
            ret, frame = cap.read()
            result = model(frame, agnostic_nms=True)[0]
            detections = sv.Detections.from_yolov8(result)
            labels = [
                f"{model.model.names[class_id]} {confidence:0.2f}"
                for _, _, confidence, class_id, _
                in detections
            ]
            frame = box_annotator.annotate(
                scene=frame, 
                detections=detections, 
                labels=labels
            ) 
            
            if self.save:
                writer.write(frame)
            
            
            cv2.imshow("yolov8", frame)

            if (cv2.waitKey(30) == 27): # break with escape key
                break
                
        cap.release()
        if self.save:
            writer.release()
        cv2.destroyAllWindows()
        
        
    def __exit__(self, exception_type, exception_value, traceback):
        # self.imageServer.close()
        cv2.destroyAllWindows()