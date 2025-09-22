from speechify import Speechify
from speechify.tts.types.get_speech_response import GetSpeechResponse
from random import randint
import base64
import os
from api.name_gen import generate_strong_name


class SpeechifyTTS:
    def __init__(self):
        api_key = os.getenv("SPEECHIFY_API_KEY")
        self.client = Speechify(token=api_key)
        self.voice_id = "jennifer"
        self.audio_dir = "audio/speechify/"


    def text_to_speech(self, usrText: str) -> str:
        audio: GetSpeechResponse = self.client.tts.audio.speech(
        input=usrText,
        voice_id=self.voice_id,
        )   
        return self._save_audio(audio=audio)


    def _save_audio(self, audio: GetSpeechResponse) -> str:

        file_format = str(audio.audio_format).lower() if audio.audio_format else "wav"
        if audio.audio_data:
            os.makedirs(self.audio_dir, exist_ok=True)
            file_path = generate_strong_name()
            file_path = self.audio_dir + file_path + f".{file_format}"
            decoded_bytes = base64.b64decode(audio.audio_data)
            with open(file_path, 'wb') as f:
                f.write(decoded_bytes)
            return file_path
        raise ValueError("No audio data returned from Speechify TTS")