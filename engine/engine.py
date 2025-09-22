from dotenv import load_dotenv; load_dotenv()
from threading import RLock
from typing import List
import os
from queue import Queue

from api.eleven_labs import ElevenLabs
from api.speechify import SpeechifyTTS
from .handle_cache import load_cache , save_cache, load_response
from tokenizer.sentence_tokenizer import split_sentences
from hash.hash_text import get_hash
from api.playAudio import  play_audio_file
 


class TTS_ENGINE:
    def __init__(self, tts_provider: str = "speechify") -> None:
        """
        Initialize the TTS engine.

        Args:
            tts_provider (str): Must be either 'elevenlabs' or 'speechify'.
        """
        tts_provider = tts_provider.lower()
        if tts_provider == "elevenlabs":
            self.tts_engine = ElevenLabs()
        elif tts_provider == "speechify":
            self.tts_engine = SpeechifyTTS()
        else:
            raise ValueError("tts_provider must be either 'elevenlabs' or 'speechify'")
            
        self.audio_cache = load_cache()
        self._cache = {}
        self._lock = RLock()
        self.audio_queue = Queue()
        
        # Analytics tracking
        self.cache_hits = 0
        self.api_calls = 0
        self.total_sentences = 0

    def set_cache(self,key, value):
        with self._lock:
            self._cache[key] = value

    def get_cache(self, key):
        with self._lock:
            return self._cache.get(key)

    def _handle_response(self, response: str) -> bool:

        if isinstance(response, str):
            sentences = split_sentences(response)
            if sentences is not None:
                for _, v in sentences:
                    self.total_sentences += 1
                    normalized_v = v.strip().lower()
                    sentence_hash = get_hash(normalized_v)
                    if sentence_hash in self._cache:
                        self.cache_hits += 1
                        print("CACHE HIT: Local audio is saved for text: ", v)
                        cached_path = self.get_cache(sentence_hash)
                        if cached_path:
                            # Check if the cached file exists
                            if os.path.exists(cached_path):
                                self.audio_queue.put(cached_path)
                            else:
                                # If WAV doesn't exist, check if MP3 exists
                                mp3_path = cached_path[:-4] + '.mp3'
                                if os.path.exists(mp3_path):
                                    print(f"WAV not found, using MP3: {mp3_path}")
                                    self.audio_queue.put(mp3_path)
                                else:
                                    print(f"Cached file not found: {cached_path}")
                    else:
                        self.api_calls += 1
                        print("CACHE MISS: TTS API is called, text: ", v)
                        audioFileLocation = self.tts_engine.text_to_speech(v)
                        if audioFileLocation:
                            if audioFileLocation.endswith('.mp3'):
                                # For MP3 files, cache the WAV path since we'll convert MP3 to WAV
                                wav_path = audioFileLocation[:-4] + '.wav'
                                self.set_cache(sentence_hash, wav_path)
                                self.audio_queue.put(audioFileLocation)  # Play the MP3 (will be converted to WAV)
                            else:
                                # For non-MP3 files, cache and play the original path
                                self.set_cache(sentence_hash, audioFileLocation)
                                self.audio_queue.put(audioFileLocation)
                return True
        return False

    def _play_audio_queue(self) -> bool:
        """Play all audio files from the queue in order, one by one."""
        if not self.audio_queue.empty():
            # Play files one by one from the queue using optimized single-file function
            while not self.audio_queue.empty():
                file_path = self.audio_queue.get()
                success = play_audio_file(file_path)
                if not success:
                    print(f"Failed to play audio file: {file_path}")
            
            save_cache(self._cache)
            return True
        return False

    def orchestration(self, text):
        if text:
            check = self._handle_response(text)
            # if check:
            #     check = self._play_audio_queue()
            #     if check:
            #         print("RUN SUCCESSFULL...")
    
    def orchestration_realtime(self, text):
        """Alternative orchestration that plays audio immediately as it's generated."""
        if text:
            sentences = split_sentences(text)
            if sentences is not None:
                for _, v in sentences:
                    self.total_sentences += 1
                    normalized_v = v.strip().lower()
                    sentence_hash = get_hash(normalized_v)
                    
                    if sentence_hash in self._cache:
                        self.cache_hits += 1
                        print("CACHE HIT: Local audio is saved for text: ", v)
                        cached_path = self.get_cache(sentence_hash)
                        if cached_path:
                            # Check if the cached file exists
                            if os.path.exists(cached_path):
                                play_audio_file(cached_path)
                            else:
                                # If WAV doesn't exist, check if MP3 exists
                                mp3_path = cached_path[:-4] + '.mp3'
                                if os.path.exists(mp3_path):
                                    print(f"WAV not found, using MP3: {mp3_path}")
                                    play_audio_file(mp3_path)
                                else:
                                    print(f"Cached file not found: {cached_path}")
                    else:
                        self.api_calls += 1
                        print("CACHE MISS: TTS API is called")
                        audioFileLocation = self.tts_engine.text_to_speech(v)
                        if audioFileLocation:
                            if audioFileLocation.endswith('.mp3'):
                                # For MP3 files, cache the WAV path since we'll convert MP3 to WAV
                                wav_path = audioFileLocation[:-4] + '.wav'
                                self.set_cache(sentence_hash, wav_path)
                            else:
                                # For non-MP3 files, cache the original path
                                self.set_cache(sentence_hash, audioFileLocation)
                            
                            # Play immediately
                            play_audio_file(audioFileLocation)
                
                save_cache(self._cache)
                print("RUN SUCCESSFULL...")

    def get_analytics(self):
        """Get analytics summary of cache performance."""
        if self.total_sentences == 0:
            return {
                'total_sentences': 0,
                'cache_hits': 0,
                'api_calls': 0,
                'cache_hit_ratio': 0.0,
                'api_call_ratio': 0.0
            }
        
        cache_hit_ratio = (self.cache_hits / self.total_sentences) * 100
        api_call_ratio = (self.api_calls / self.total_sentences) * 100
        
        return {
            'total_sentences': self.total_sentences,
            'cache_hits': self.cache_hits,
            'api_calls': self.api_calls,
            'cache_hit_ratio': round(cache_hit_ratio, 2),
            'api_call_ratio': round(api_call_ratio, 2)
        }
    
    def print_analytics(self):
        """Print formatted analytics summary."""
        analytics = self.get_analytics()
        
        print("\n" + "="*50)
        print("📊 TTS ENGINE ANALYTICS")
        print("="*50)
        print(f"Total Sentences Processed: {analytics['total_sentences']}")
        print(f"Cache Hits: {analytics['cache_hits']} ({analytics['cache_hit_ratio']}%)")
        print(f"API Calls: {analytics['api_calls']} ({analytics['api_call_ratio']}%)")
        print("="*50)
        
        if analytics['cache_hit_ratio'] > 50:
            print("🎉 Great cache performance! More than 50% cache hits.")
        elif analytics['cache_hit_ratio'] > 25:
            print("✅ Good cache performance! More than 25% cache hits.")
        else:
            print("⚠️  Low cache performance. Consider optimizing cache strategy.")
        print("="*50 + "\n")

def run_simulation():
    engine = TTS_ENGINE()

    responses = load_response()

    for text in responses:
        engine.orchestration(text=text)
    
    # Display analytics after processing all responses
    engine.print_analytics()

