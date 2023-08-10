from google.cloud import texttospeech
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credential/google_cloud_credentials.json'


class TextToSpeechClient:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
    
    def text_to_mp3(self, voice_name: str, text: str):
        synthesis_input = texttospeech.SynthesisInput(text="Hello, World!")

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )


        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')
    

if __name__ == "__main__":
    client = TextToSpeechClient()
    client.text_to_mp3("en-US-Wavenet-D", "Hello World")