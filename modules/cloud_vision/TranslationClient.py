from google.cloud import translate_v2 as translate
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/google_cloud_credentials.json'

class TranslationClient:
    def __init__(self):
        self.client = translate.Client()
    
    # returns [input, translatedText, detectedSourceLanguage]
    def translate_text(self, target: str, text: str) -> dict:

        if isinstance(text, bytes):
            text = text.decode("utf-8")
        
        # to get the target language codes
        # results = self.client.get_languages()

        # for language in results:
        #     print("{name} ({language})".format(**language))

  
        result = self.client.translate(text, target_language=target)
        

        # print("Text: {}".format(result["input"]))
        # print("Translation: {}".format(result["translatedText"]))
        # print("Detected source language: {}".format(result["detectedSourceLanguage"]))

        return result

if __name__ == "__main__":
    client = TranslationClient()
    client.translate_text("fr", "Hello World")
