import cv2
import supervision as sv
from ultralytics import YOLO
import time

from ObjectDetectionCounter import ObjectDetectionCounter
from VideoStream import VideoStream

class VideoDetection:
    def __init__(
            self,
            video_path=0,
            inference=True,
            confidence_level=0.7,
            model="./modules/yolov8/weights/model.pt",
            save=False,
            save_path="yolo_video_output.avi",
            object_counter_duration = 1, # set object detection counter duration
    ):
        self.videoPath = video_path
        self.inference = inference
        self.confidenceLevel = confidence_level
        self.model = model
        self.useWebcam = False
        self.useStream = False
        self.captureInProgress = False
        self.save = save
        self.savePath = save_path
        self.capture = None
        self.stream = None
        self.last_detection = None

        if object_counter_duration > 0:
            self.object_detection_counter = ObjectDetectionCounter(object_counter_duration)
        else:
            self.object_detection_counter = None


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
            self.capture = cv2.VideoCapture(new_video_path)
            if self.capture.isOpened():
                self.captureInProgress = True
        elif self.useStream:
            print("   - Using stream")
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

        if self.useStream:
            camera_fps = int(self.stream.stream.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        elif self.useWebcam:
            camera_fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if camera_fps == 0:
            print("Error : Could not get FPS")
            return

        # to save the video
        if self.save:
            writer = cv2.VideoWriter(self.savePath,
                                     cv2.VideoWriter_fourcc(*'DIVX'),
                                     camera_fps,
                                     (frame_width, frame_height))

        # specify the model
        model = YOLO(self.model)

        # customize the bounding box
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )

        while True:
            if not self.captureInProgress:
                break

            try:
                if self.useStream:
                    frame = self.stream.read()
                else:
                    frame = self.capture.read()[1]
            except Exception as e:
                print("ERROR : Exception during capturing")
                raise(e)

            #  iou=0.45, max_det=50, verbose=False
            result = model(frame, agnostic_nms=True, conf=self.confidenceLevel, verbose=False)[0]
            # [[bounding_boxes, mask, confidence, class_id, tracker_id]
            detections = sv.Detections.from_yolov8(result)

            # [[class_label, confidence, bounding_boxes]]
            detection_results = [
                [model.model.names[class_id], confidence, bounding_boxes]
                for bounding_boxes, _, confidence, class_id, _ in detections
            ]
            labels = [f'{class_label} {confidence:0.2f}' for class_label, confidence, _ in
                      detection_results]

            frame = box_annotator.annotate(
                scene=frame,
                detections=detections,
                labels=labels
            )

            if self.object_detection_counter:
                self.object_detection_counter.infer_counting(detection_results)

            self.last_detection = detection_results

            if self.save:
                writer.write(frame)

            cv2.imshow("YOLOv8", frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):  # break with q key
                break

        if self.save:
            writer.release()

    def get_last_detection(self):
        return self.last_detection

    def __exit__(self, exception_type, exception_value, traceback):

        if self.capture:
            self.capture.release()

        if self.stream:
            self.stream.stop()

        cv2.destroyAllWindows()


