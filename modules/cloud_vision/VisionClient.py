from google.cloud import vision
import pandas as pd
import os
import sys

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/cloud_vision_credentials.json'


class VisionClient:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def annotate_image(self, image_uri, log=False):
        response = self.client.annotate_image({
            'image': {
                'source': {
                    'image_uri': image_uri
                }
            }
        })

        if log:
            print("response : ", response)

        return self._decode_response(response)

    def _decode_response(self, response):

        # Preprocessing for visualization. 
        descriptions = []
        scores = []
        for label in response.label_annotations:
            descriptions.append(label.description)
            scores.append(label.score)

        dic = {"description": descriptions, "score": scores}

        print(dic)

        return dic

    def _detect_text_image(self, google_vision_image):
        response = self.client.text_detection(image=google_vision_image)
        texts = response.text_annotations
        print("Texts:")

        for text in texts:
            print(f'\n"{text.description}"')

            vertices = [
                f"({vertex.x},{vertex.y})" for vertex in text.bounding_poly.vertices
            ]

            print("bounds: {}".format(",".join(vertices)))

        if response.error.message:
            raise Exception(
                f"{response.error.message}\nFor more info on error messages, check: https://cloud.google.com/apis/design/errors")

        return texts

    def detect_text_image_file(self, image_path):
        """Detects text in the file."""

        with open(image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        return self._detect_text_image(image)

    def detect_text_image_uri(self, uri):
        """Detects text in the file located in Google Cloud Storage or on the Web."""

        image = vision.Image()
        image.source.image_uri = uri

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
