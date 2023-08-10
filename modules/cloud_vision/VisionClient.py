from google.cloud import vision
import cv2
import pandas as pd
import os
import sys

#import modules.utilities.image_utility as image_utility

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/google_cloud_credentials.json'


class VisionClient:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    # return a [descriptions, scores, vertices] list
    def _detect_text_image(self, google_vision_image):
        print("_detect_text_image")

        response = self.client.text_detection(image=google_vision_image)
        annotations = response.text_annotations
        print("Texts:")

        descriptions = []
        scores = []
        vertices = []

        for annotation in annotations:
            descriptions.append(annotation.description)
            scores.append(annotation.score)
            vertices.append(annotation.bounding_poly.vertices)

        if response.error.message:
            raise Exception(
                f"{response.error.message}\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors")

        return descriptions, scores, vertices

    def detect_text_image_bytes(self, image_bytes):
        image = vision.Image(content=image_bytes)

        return self._detect_text_image(image)

    def detect_text_image_file(self, image_path):
        return self.detect_text_image_bytes(image_utility.read_image_file_bytes(image_path))

    def detect_text_image_uri(self, uri):
        image = vision.Image()
        image.source.image_uri = uri

        return self._detect_text_image(image)

    # detect text in a image using document text detection
    def detect_dense_text(self, image_path):
        """Detects document features in an image."""

        
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = self.client.document_text_detection(image=image)

        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                print('\nBlock confidence: {}\n'.format(block.confidence))

                for paragraph in block.paragraphs:
                    print('Paragraph confidence: {}'.format(
                        paragraph.confidence))

                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        print('Word text: {} (confidence: {})'.format(
                            word_text, word.confidence))

    # FIXME: extract lower methods, detect_landmarks_image_bytes, detect_landmarks_image_file
    # detect landmarks in a image
    def detect_landmarks(self, image_path):
        """Detects landmarks in the file."""

        image = vision.Image(content=image_utility.read_image_file_bytes(image_path))

        response = self.client.landmark_detection(image=image)
        landmarks = response.landmark_annotations

        descriptions = []
        scores = []
        bounding_boxes = []

        for landmark in landmarks:
            descriptions.append(landmark.description)
            scores.append(landmark.score)
            bounding_boxes.append(landmark.bounding_poly.vertices)

        return descriptions, scores, bounding_boxes

    def detect_objects(self, image_path):
        """Detects objects in the file."""

        image = vision.Image(content=image_utility.read_image_file_bytes(image_path))

        objects = self.client.object_localization(
            image=image).localized_object_annotations

        descriptions = []
        scores = []
        bounding_boxes = []

        for object_ in objects:
            descriptions.append(object_.name)
            scores.append(object_.score)
            bounding_boxes.append(object_.bounding_poly.vertices)

        return descriptions, scores, bounding_boxes

    def get_multiple_detections(self, image_path):
        """Detects labels in the file."""

        image = vision.Image(content=image_utility.read_image_file_bytes(image_path))

        features = [
            vision.Feature.Type.OBJECT_LOCALIZATION,
            vision.Feature.Type.TEXT_DETECTION,
            vision.Feature.Type.DOCUMENT_TEXT_DETECTION,
        ]

        request = {
            "image": image,
            "features": [
                {"type_": vision.Feature.Type.TEXT_DETECTION},
                {"type_": vision.Feature.Type.OBJECT_LOCALIZATION},
            ],
        }

        response = self.client.annotate_image(request)

        print(response)

        descriptions = []
        scores = []
        bounding_boxes = []

        for object_localization in response.localized_object_annotations:
            descriptions.append(object_localization.name)
            scores.append(object_localization.score)
            bounding_boxes.append(object_localization.bounding_poly.vertices)

        for text in response.text_annotations:
            descriptions.append(text.description)
            scores.append(text.score)
            bounding_boxes.append(text.bounding_poly.vertices)

        return descriptions, scores, bounding_boxes


if __name__ == '__main__':
    vision_client = VisionClient()
    # vision_client.detect_dense_text("test_images/IMG_20210814_141230.jpg")
    # vision_client.detect_landmarks("test_images/IMG_20210814_141230.jpg")
    # vision_client.detect_objects("test_images/IMG_20210814_141230.jpg")
    vision_client.detect_dense_text("med1.jpg")

