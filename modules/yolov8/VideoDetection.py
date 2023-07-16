import cv2
import supervision as sv
from ultralytics import YOLO
import time
import numpy as np

from ObjectDetectionCounter import ObjectDetectionCounter
from VideoStream import VideoStream


class VideoDetection:
    def __init__(
            self,
            video_path=0,
            inference=True, # set to False to hide object detection
            confidence_level=0.65,
            model="./modules/yolov8/weights/model.pt",
            save=False,
            save_path="yolo_video_output.avi",
            object_counter_duration=0,  # set object detection counter duration
            # [x1, y1, x2, y2]  the detection region on which detection results should be reported
            detection_region=None,

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
        self.detection_region = detection_region
        self.capture = None
        self.stream = None
        self.last_detection = None
        self.class_labels = None

        if object_counter_duration > 0:
            self.object_detection_counter = ObjectDetectionCounter(object_counter_duration)
        else:
            self.object_detection_counter = None

        self.camera_fps = None
        self.frame_height = None
        self.frame_width = None
        self.last_frame = None

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
            return self.object_detection_counter.get_detected_object_percentage()

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
            time.sleep(1.0)  # wait until loading at least one frame
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

        camera_fps = None
        frame_width = None
        frame_height = None

        if self.useStream:
            camera_fps = int(self.stream.stream.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        elif self.useWebcam:
            camera_fps = int(self.capture.get(cv2.CAP_PROP_FPS))
            frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if camera_fps is None:
            print("Error : Could not get FPS")
            return

        print(f"Camera FPS:{camera_fps}, width:{frame_width}, height:{frame_height}")
        self.camera_fps = camera_fps
        self.frame_width = frame_width
        self.frame_height = frame_height

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
                raise (e)

            # save the last captured frame
            self.last_frame = frame

            #  iou=0.45, max_det=50, verbose=False
            result = model(frame, agnostic_nms=True, conf=self.confidenceLevel, verbose=False)[0]
            # [[bounding_boxes, mask, confidence, class_id, tracker_id]
            detections = sv.Detections.from_yolov8(result)

            # class labels
            self.class_labels = model.model.names

            # only consider the detections in the selected region, also see https://roboflow.github.io/supervision/quickstart/detections/
            if self.detection_region is not None:
                detections = self.get_detection_in_region(detections, self.detection_region)

            # show inference results if needed
            if self.inference:
                labels = [f'{self.class_labels[class_id]} {confidence:0.2f}' for
                          _, _, confidence, class_id, _ in detections]

                frame = box_annotator.annotate(
                    scene=frame,
                    detections=detections,
                    labels=labels
                )

            if self.object_detection_counter:
                self.object_detection_counter.infer_counting(detections, self.class_labels)

            self.last_detection = detections

            if self.save:
                writer.write(frame)

            cv2.imshow("YOLOv8", frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):  # break with q key
                break

        if self.save:
            writer.release()

    # return results in the format of [[class_label, confidence, bounding_boxes]] from the detections in the format of [[bounding_boxes, mask, confidence, class_id, tracker_id]]
    @staticmethod
    def get_detection_results(detections, model_class_names):
        detection_results = [
            [model_class_names[class_id], confidence, bounding_boxes]
            for bounding_boxes, _, confidence, class_id, _ in detections
        ]
        return detection_results

    @staticmethod
    def get_detection_in_region(detections, detection_region, exclude_class_ids=[]):

        # initialize a instance of Detection class with empty values
        detections_in_specified_region = sv.Detections(xyxy=np.empty((0, 4)), mask=None,
                                                       confidence=np.empty((0,)),
                                                       class_id=np.empty((0,)),
                                                       tracker_id=None)
        # create temporary lists to store the values of xyxy, class_id and confidence of the objects in given region
        tmp_xyxy = []
        tmp_class_id = []
        tmp_confidence = []

        # [bounding_boxes, mask, confidence, class_id, tracker_id]
        for detection in detections:
            bounding_boxes = detection[0]
            class_id = detection[3]
            confidence = detection[2]
            # add to detection_results only if the object is in the specified region and not in exclude_class_ids
            if class_id not in exclude_class_ids and VideoDetection.intersects(bounding_boxes, detection_region):
                tmp_xyxy.append(bounding_boxes)
                tmp_class_id.append(class_id)
                tmp_confidence.append(confidence)

        detections_in_specified_region.xyxy = np.array(tmp_xyxy)
        detections_in_specified_region.class_id = np.array(tmp_class_id)
        detections_in_specified_region.confidence = np.array(tmp_confidence)

        return detections_in_specified_region

    # return the last captured frame (an image array vector)
    def get_last_frame(self):
        return self.last_frame

    # return [camera_fps, frame_width, frame_height, is_stream]
    def get_source_params(self):
        return self.camera_fps, self.frame_width, self.frame_height, self.useStream

    @staticmethod
    def intersects(xyxy, xyxy_bounds):
        return not (xyxy[2] < xyxy_bounds[0] or xyxy[0] > xyxy_bounds[2] or xyxy[3] < xyxy_bounds[
            1] or xyxy[1] > xyxy_bounds[3])

    @staticmethod
    def is_inside(xy, xyxy):
        p_x, p_y = xy
        min_x, min_y, max_x, max_y = xyxy
        return min_x < p_x < max_x and min_y < p_y < max_y

    # return the last detection results in the format of [[bounding_boxes, mask, confidence, class_id, tracker_id], ...]
    def get_last_detection(self):
        return self.last_detection

    # return the class labels of the model, [name1, name2, ...]
    def get_class_labels(self):
        return self.class_labels

    def __exit__(self, exception_type, exception_value, traceback):

        if self.capture:
            self.capture.release()

        if self.stream:
            self.stream.stop()

        cv2.destroyAllWindows()
