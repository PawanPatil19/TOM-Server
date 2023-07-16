from google.cloud import vision
import cv2
import pandas as pd
import os
import sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/cloud_vision_credentials.json'


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

    def detect_text_image_file(self, image_path):
        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        return self._detect_text_image(image)

    def detect_text_image_uri(self, uri):
        image = vision.Image()
        image.source.image_uri = uri

        return self._detect_text_image(image)

    def detect_text_frame(self, opencv_frame):
        _, encoded_image = cv2.imencode('.png', opencv_frame)
        image_content = encoded_image.tobytes()

        image = vision.Image(content=image_content)

        return self._detect_text_image(image)

    # detect text in a image using document text detection
    def detect_dense_text(self, image_path):
        """Detects document features in an image."""

        with open(image_path, 'rb') as image_file:
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
