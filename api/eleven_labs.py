from elevenlabs.client import ElevenLabs as ElevenLabsClient
from random import randint
import os

class ElevenLabs:
    def __init__(self, api_key):
        self.client = ElevenLabsClient(api_key=api_key)
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"
        self.model_id = "eleven_multilingual_v2"
        self.output_format="mp3_44100_128"
        self.audio_dir = "./audio"

    def text_to_speech(self, usrText: str):
        audio = self.client.text_to_speech.convert(
            text=usrText,
            voice_id= self.voice_id,
            model_id=self.model_id,
            output_format=self.output_format,
        )

        os.makedirs(self.audio_dir, exist_ok=True)
        with open(f'{self.audio_dir}/{randint(0, 10000)}.mp3', 'wb') as f:
            for chunk in audio:
                f.write(chunk)

