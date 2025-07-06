import os
import time
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
import openai
from elevenlabs import generate, play, save, set_api_key

class VoiceHandler:
    def __init__(self, voice_id=None):
        # Set API key for ElevenLabs
        set_api_key(os.getenv("ELEVENLABS_API_KEY"))
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Set voice ID (use default if not provided)
        self.voice_id = voice_id if voice_id else "21m00Tcm4TlvDq8ikWAM"
        
        # Create recordings directory if it doesn't exist
        os.makedirs("recordings", exist_ok=True)
        
        # Set audio parameters
        self.sample_rate = 44100
        
    def text_to_speech(self, text):
        """Convert text to speech using ElevenLabs API"""
        try:
            # Generate audio from text
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Save audio to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file_path = temp_file.name
            save(audio, temp_file_path)
            
            # Play the audio
            data, samplerate = sf.read(temp_file_path)
            sd.play(data, samplerate)
            sd.wait()
            
            # Save a copy to recordings folder with timestamp
            timestamp = int(time.time())
            recording_path = f"recordings/ai_response_{timestamp}.wav"
            save(audio, recording_path)
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            return True
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            return False
    
    def speech_to_text(self, duration=5):
        """Record audio and convert to text using OpenAI's Whisper API"""
        try:
            print("Recording... Speak now.")
            
            # Record audio
            recording = sd.rec(int(duration * self.sample_rate), 
                              samplerate=self.sample_rate,
                              channels=1)
            sd.wait()
            
            # Save recording to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            sf.write(temp_file.name, recording, self.sample_rate)
            
            # Convert audio to text using OpenAI's Whisper
            with open(temp_file.name, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # Clean up the temporary file
            os.unlink(temp_file.name)
            
            return transcript.text
        except Exception as e:
            print(f"Error in speech-to-text: {e}")
            return ""








