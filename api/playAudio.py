import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import os

def play_audio(file_list: list[str]):

    for file in file_list:
        print(f"Playing: {file}")
        ext = os.path.splitext(file)[1].lower()

        # Convert MP3 -> WAV on the fly
        if ext == ".mp3":
            audio = AudioSegment.from_mp3(file)
            wav_file = f"{file.split('.')[0]}.wav"
            audio.export(wav_file, format="wav")

            # Play with sounddevice
            data, samplerate = sf.read(wav_file)
            sd.play(data, samplerate)
            # Clean up temp file
            if os.path.exists(file):
                os.remove(file)
            sd.wait()
        else:
            data, samplerate = sf.read(file)
            sd.play(data, samplerate)
            sd.wait()

if __name__ == "__main__":
    # Example usage
    files = ["audio/speechify/470453.wav",]
    play_audio(files)   
