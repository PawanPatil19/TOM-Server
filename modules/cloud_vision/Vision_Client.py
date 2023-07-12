from google.cloud import vision
import pandas as pd
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/cloud_vision_credentials.json'

class VisionClient:
    def __init__(self, image_path):
        self.client = self.vision_client()
        self.image_path = image_path
        

    def vision_client(self):
        """Create vision client."""
        return vision.ImageAnnotatorClient()

    def annotate_image(self, vision_client, image_uri, log=False):

        response = self.client.annotate_image({
        'image': {
            'source': {
                'image_uri': image_uri
            }
        }
        })
        
        if log:
            print("response : ", response)
            
        return response

    def visualization(self, response):

        # Preprocessing for visualization. 
        descriptions = []
        scores = []
        for label in response.label_annotations:
            descriptions.append(label.description)
            scores.append(label.score)

        dic = {"description": descriptions, "score": scores}



    def detect_text(self):
        """Detects text in the file."""

        with open(self.image_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = self.client.text_detection(image=image)
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
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )

    def detect_text_uri(self):
        """Detects text in the file located in Google Cloud Storage or on the Web."""
        
        image = vision.Image()
        image.source.image_uri = self.image_path

        response = self.client.text_detection(image=image)
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
                "{}\nFor more info on error messages, check: "
                "https://cloud.google.com/apis/design/errors".format(response.error.message)
            )


    # detect text in a image using document text detection
    def detect_dense_text(self) :
        """Detects document features in an image."""
        client = vision.ImageAnnotatorClient()

        with open(self.image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.document_text_detection(image=image)

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



if __name__ == "__main__":
    vision_client = VisionClient("img.png")
    vision_client.detect_text_in_document()

       
    