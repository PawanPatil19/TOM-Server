from typing import Any
from google.cloud import translate_v2 as translate
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/google_cloud_credentials.json'

class TranslationClient:
    def __init__(self):
        self.client = translate.Client()
        self.language_dict = {}
        
    # create dictionary with name and target language code
    def create_language_dict(self):
        for language in self.client.get_languages():
            self.language_dict[language["name"]] = language["language"]
        
        return self.language_dict

    def get_language_code(self, language_name: str) -> str:
        return self.language_dict[language_name]

    # returns [input, translatedText, detectedSourceLanguage]
    def translate_text(self, target: str, text: str) -> dict:

        if isinstance(text, bytes):
            text = text.decode("utf-8")
  
        result = self.client.translate(text, target_language=target)
    
        

        # print("Text: {}".format(result["input"]))
        # print("Translation: {}".format(result["translatedText"]))
        # print("Detected source language: {}".format(result["detectedSourceLanguage"]))

        return result

if __name__ == "__main__":
    client = TranslationClient()
    create_language_dict = client.create_language_dict()
    target_language_code = client.get_language_code("French")
    print(client.translate_text(target_language_code, "Hello World"))
