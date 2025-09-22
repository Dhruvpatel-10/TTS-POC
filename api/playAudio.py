import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import os

def play_audio_file(file_path: str) -> bool:
    """
    Play a single audio file. Optimized for queue-based approach.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        bool: True if file was played successfully, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return False
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        # Handle MP3 files - convert to WAV first
        if ext == ".mp3":
            print(f"Converting and playing: {file_path}")
            audio = AudioSegment.from_mp3(file_path)
            wav_file = f"{file_path.split('.')[0]}.wav"
            
            # Export to WAV format
            audio.export(wav_file, format="wav")
            print(f"Playing: {wav_file}")
            
            # Play the WAV file with sounddevice
            data, samplerate = sf.read(wav_file)
            sd.play(data, samplerate)
            sd.wait()
            
            # Clean up the original MP3 file (keep the WAV for future use)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed original MP3 file: {file_path}")
                
        # Handle WAV files directly
        elif ext == ".wav":
            print(f"Playing: {file_path}")
            data, samplerate = sf.read(file_path)
            sd.play(data, samplerate)
            sd.wait()
        else:
            print(f"Unsupported audio format: {ext} for file: {file_path}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error playing audio file {file_path}: {e}")
        return False

def play_audio(file_list: list[str]):
    """
    Legacy function for backward compatibility.
    Now uses the optimized single-file approach.
    """
    for file_path in file_list:
        play_audio_file(file_path)

def play_audio_stream(file_paths: list[str], continuous: bool = True):
    """
    Stream audio files continuously for better queue-based experience.
    
    Args:
        file_paths (list[str]): List of audio file paths
        continuous (bool): If True, plays files continuously without gaps
    """
    for i, file_path in enumerate(file_paths):
        success = play_audio_file(file_path)
        if not success:
            print(f"Skipping failed file: {file_path}")
            continue
            
        # Add small gap between files if not continuous
        if not continuous and i < len(file_paths) - 1:
            import time
            time.sleep(0.1)  # 100ms gap between files
        
if __name__ == "__main__":
    # Example usage
    files = ["audio/speechify/470453.wav",]
    play_audio(files)   
