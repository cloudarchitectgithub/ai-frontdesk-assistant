import os
import time
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
import openai
import threading
from elevenlabs import ElevenLabs
import queue
import pyttsx3
from typing import Optional

def get_mac_audio_devices():
    """Get Mac mic and speakers device IDs"""
    try:
        devices = sd.query_devices()
        mac_mic = None
        mac_speakers = None
        
        for i, device in enumerate(devices):
            if 'MacBook Pro Microphone' in device['name'] and device['max_input_channels'] > 0:
                mac_mic = i
            if 'MacBook Pro Speakers' in device['name'] and device['max_output_channels'] > 0:
                mac_speakers = i
        
        return mac_mic, mac_speakers
        
    except Exception as e:
        print(f"Error getting Mac audio devices: {e}")
        return None, None

class VoiceHandler:
    def __init__(self, use_elevenlabs=True):
        """Initialize voice handler with option to use ElevenLabs or fallback"""
        self.use_elevenlabs = use_elevenlabs
        
        # Get available audio devices
        devices = get_mac_audio_devices()
        
        # Set up Mac microphone and speakers
        self.input_device = 2  # MacBook Pro Microphone
        self.output_device = 3  # MacBook Pro Speakers
        self.sample_rate = 16000
        
        print(f"Using Mac devices - Input: {self.input_device} (MacBook Pro Microphone), Output: {self.output_device} (MacBook Pro Speakers)")
        
        # Initialize ElevenLabs client if enabled
        if self.use_elevenlabs:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
                self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Jessica voice
                print("ElevenLabs client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize ElevenLabs: {e}")
                print("Falling back to macOS speech synthesis")
                self.use_elevenlabs = False
        else:
            print("Using macOS speech synthesis (ElevenLabs disabled)")
        
        # Recording state
        self.recording_active = False
        self.stop_recording = threading.Event()
        
        # Call recording
        self.call_recording_active = False
        self.call_audio_segments = []
        self.call_start_time = None
        
        # Create recordings directory if it doesn't exist
        os.makedirs("recordings", exist_ok=True)
        
        try:
            # Initialize text-to-speech engine
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            
            # Try to find female voice on macOS (usually Samantha)
            for voice in voices:
                if "samantha" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    print(f"Using voice: {voice.name}")
                    break
            
            # Configure speech properties
            self.engine.setProperty('rate', 150)    # Speed - not too fast
            self.engine.setProperty('volume', 1.0)  # Full volume
            
            # Set up audio device parameters
            self.sample_rate = 44100
            self.channels = 1
            
            print("Voice handler initialized successfully with pyttsx3")
            
        except Exception as e:
            print(f"Error initializing voice handler: {e}")
            raise

    def start_call_recording(self):
        """Start recording the entire call"""
        self.call_recording_active = True
        self.call_audio_segments = []
        self.call_start_time = time.time()
        print("🎙️ Call recording started...")

    def stop_call_recording(self):
        """Stop recording and save the complete call"""
        if not self.call_recording_active:
            return
        
        self.call_recording_active = False
        
        if not self.call_audio_segments:
            print("No call audio to save.")
            return
        
        try:
            # Combine all audio segments
            combined_audio = np.concatenate(self.call_audio_segments)
            
            # Generate timestamp for filename
            timestamp = int(self.call_start_time)
            call_duration = int(time.time() - self.call_start_time)
            
            # Save the complete call recording
            call_filename = f"recordings/complete_call_{timestamp}_{call_duration}s.wav"
            sf.write(call_filename, combined_audio, self.sample_rate)
            
            print(f"🎙️ Complete call saved: {call_filename}")
            print(f"📊 Call duration: {call_duration} seconds")
            
            # Clear the segments to free memory
            self.call_audio_segments = []
            
        except Exception as e:
            print(f"Error saving call recording: {e}")

    def add_to_call_recording(self, audio_data):
        """Add audio segment to the call recording"""
        if self.call_recording_active and audio_data is not None:
            # Ensure audio data is 1D
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            self.call_audio_segments.append(audio_data)

    def text_to_speech(self, text):
        """Convert text to speech using ElevenLabs with Jessica voice, with fallback to macOS speech"""
        if not self.use_elevenlabs:
            return self._fallback_text_to_speech(text)
        
        try:
            print("Converting text to speech using ElevenLabs Jessica...")
            
            # Generate audio from text using ElevenLabs
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text
            )
            audio_bytes = b"".join(audio_generator)
            
            # Save audio to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_file_path = temp_file.name
            temp_file.write(audio_bytes)
            temp_file.close()
            
            # Load the audio data
            data, samplerate = sf.read(temp_file_path)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # ElevenLabs generates at 44.1kHz, ensure we play at the correct rate
            print(f"ElevenLabs audio: {samplerate} Hz, {len(data)} samples")
            
            # Ensure data is float32 for proper playback
            if data.dtype != np.float32:
                data = data.astype(np.float32)
            
            # Add to call recording if active (resample to 16kHz for consistency)
            if self.call_recording_active:
                try:
                    from scipy import signal
                    # Resample to 16kHz for call recording
                    resampled_data = signal.resample(data, int(len(data) * self.sample_rate / samplerate))
                    self.add_to_call_recording(resampled_data)
                except ImportError:
                    print("Note: scipy not available, using original audio for call recording")
                    self.add_to_call_recording(data)
            
            # Play the audio at the original ElevenLabs sample rate (44.1kHz)
            print(f"Playing audio at {samplerate} Hz sample rate...")
            sd.play(data, samplerate, device=self.output_device)
            sd.wait()
            
            # Clean up the temporary file
            os.unlink(temp_file_path)
            
            print("Audio playback complete")
            return True
            
        except Exception as e:
            print(f"Error in ElevenLabs text-to-speech: {e}")
            print("Falling back to macOS speech synthesis...")
            return self._fallback_text_to_speech(text)

    def _fallback_text_to_speech(self, text):
        """Fallback text-to-speech using macOS built-in speech synthesis"""
        try:
            print("Using macOS speech synthesis...")
            
            # Use macOS say command for text-to-speech (simpler approach)
            import subprocess
            
            # Use a simpler command that should work better
            cmd = [
                'say',
                '-v', 'Samantha',  # Use a female voice similar to Jessica
                '-r', '150',  # Slightly slower rate for clarity
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("macOS speech playback complete")
                return True
            else:
                print(f"macOS speech synthesis failed: {result.stderr}")
                # Try an even simpler approach
                return self._simple_fallback_speech(text)
                
        except Exception as e:
            print(f"Error in macOS speech synthesis: {e}")
            print("Trying simple fallback...")
            return self._simple_fallback_speech(text)

    def _simple_fallback_speech(self, text):
        """Ultra-simple fallback using basic say command"""
        try:
            print("Using simple fallback speech...")
            import subprocess
            
            # Just use the basic say command
            subprocess.run(['say', text], check=True)
            print("Simple fallback speech complete")
            return True
            
        except Exception as e:
            print(f"Simple fallback also failed: {e}")
            print("Speech synthesis failed completely. Text will be displayed only.")
            return False

    def speech_to_text(self, duration=8):
        """Enhanced speech to text with real speech recognition"""
        # Initialize temp_filepath at the beginning
        temp_filepath = None
        
        try:
            print("Recording... Speak now.")
            self.recording_active = True
            self.stop_recording.clear()
            
            # Record audio with countdown
            audio_data = self._record_with_countdown(duration)
            
            if audio_data is None:  # Recording was interrupted
                print("Recording was interrupted.")
                return ""
            
            # Add to call recording if active
            self.add_to_call_recording(audio_data)
            
            print("Recording complete. Processing...")
            
            # Save to temporary file for processing
            try:
                # Create a temporary file with a unique name
                import uuid
                temp_filename = f"temp_recording_{uuid.uuid4()}.wav"
                temp_filepath = os.path.join(tempfile.gettempdir(), temp_filename)
                sf.write(temp_filepath, audio_data, self.sample_rate)
            except Exception as e:
                print(f"Error saving recording: {e}")
                return ""
            
            # Process the audio file with OpenAI Whisper API
            try:
                # Initialize OpenAI client if not already done
                if not hasattr(self, 'openai_client'):
                    self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                # Convert audio to text using OpenAI's Whisper
                with open(temp_filepath, "rb") as audio_file:
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                transcription = transcript.text.strip()
                
                if transcription:
                    # Enhanced time format handling
                    transcription = self._improve_time_recognition(transcription)
                    return transcription
                else:
                    print("No speech detected. Please try again.")
                    return ""
                    
            except Exception as e:
                print(f"Error with OpenAI Whisper transcription: {e}")
                print("Falling back to local Whisper...")
                
                # Fallback to local Whisper
                try:
                    import whisper
                    model = whisper.load_model("base")
                    result = model.transcribe(temp_filepath)
                    transcription = result["text"].strip()
                    
                    if transcription:
                        # Enhanced time format handling
                        transcription = self._improve_time_recognition(transcription)
                        return transcription
                    else:
                        print("No speech detected. Please try again.")
                        return ""
                        
                except Exception as e2:
                    print(f"Error with local Whisper transcription: {e2}")
                    print("Speech recognition failed. Falling back to manual input...")
                    
                    # Final fallback to manual input
                    try:
                        print("Please type what you want to say:")
                        manual_input = input("> ").strip()
                        if manual_input:
                            return self._improve_time_recognition(manual_input)
                        return ""
                    except KeyboardInterrupt:
                        print("\nInput cancelled.")
                        return ""
            
        except KeyboardInterrupt:
            print("\nRecording interrupted by user.")
            self.recording_active = False
            return ""
        except Exception as e:
            print(f"Error during recording: {e}")
            return ""
        finally:
            self.recording_active = False
            # Make sure we always try to clean up the temp file
            if temp_filepath and os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass  # Ignore errors during cleanup

    def _improve_time_recognition(self, text):
        """Improve time format recognition for better appointment scheduling"""
        import re
        
        # Convert various time formats to standard format
        text = text.lower().strip()
        
        # Normalize all possible delimiters to colon
        text = re.sub(r'(\d{1,2})[\s\.-](\d{2})(:00)?\s*(am|pm)', r'\1:\2 \4', text, flags=re.IGNORECASE)
        
        # Remove any redundant :00 after a valid time (including multiple :00)
        text = re.sub(r'(\d{1,2}:\d{2})(:00)+', r'\1', text)
        
        # Handle "11 a.m." -> "11:00 AM"
        text = re.sub(r'(\d{1,2})\s*(a\.m\.|am|a\.m|p\.m\.|pm|p\.m)', r'\1:00 \2', text, flags=re.IGNORECASE)
        
        # Handle "115 pm" -> "1:15 PM" (single digit hour)
        text = re.sub(r'^(\d{1})(\d{2})\s*(am|pm)', r'\1:\2 \3', text, flags=re.IGNORECASE)
        # Handle "1115 pm" -> "11:15 PM" (double digit hour)
        text = re.sub(r'^(\d{2})(\d{2})\s*(am|pm)', r'\1:\2 \3', text, flags=re.IGNORECASE)
        
        # Handle "one fifteen pm" -> "1:15 PM"
        number_words = {
            'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
            'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
            'eleven': '11', 'twelve': '12'
        }
        for word, num in number_words.items():
            text = text.replace(f'{word} fifteen', f'{num}:15')
            text = text.replace(f'{word} thirty', f'{num}:30')
            text = text.replace(f'{word} forty five', f'{num}:45')
            text = text.replace(f'{word} forty-five', f'{num}:45')
        
        # Remove any double colons (edge case)
        text = re.sub(r':+', ':', text)
        # Remove any trailing or leading colons or spaces
        text = text.strip(' :')
        
        # Final cleanup: if still has ':00' at the end, remove it
        text = re.sub(r'(\d{1,2}:\d{2}):00', r'\1', text)
        
        # Capitalize AM/PM
        text = re.sub(r'\b(am|pm)\b', lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)
        
        print(f"Processed text: '{text}'")
        return text

    def _record_with_countdown(self, duration: int) -> Optional[np.ndarray]:
        """Record audio with interruptible countdown"""
        try:
            # Start recording in a separate thread
            audio_data = []
            
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"Audio status: {status}")
                audio_data.append(indata.copy())
            
            # Start recording
            with sd.InputStream(callback=audio_callback, 
                              device=self.input_device,
                              samplerate=self.sample_rate,
                              channels=1,
                              dtype='int16'):
                
                # Countdown with interrupt checking
                for remaining in range(duration, 0, -1):
                    if self.stop_recording.is_set():
                        return None
                    print(f"Recording: {remaining} seconds remaining...")
                    
                    # Use interruptible sleep
                    for _ in range(10):  # 100ms intervals
                        if self.stop_recording.is_set():
                            return None
                        time.sleep(0.1)
            
            return np.concatenate(audio_data) if audio_data else None
            
        except KeyboardInterrupt:
            self.stop_recording.set()
            return None
        except Exception as e:
            print(f"Error during recording: {e}")
            return None

    def stop_current_recording(self):
        """Method to gracefully stop current recording"""
        if self.recording_active:
            self.stop_recording.set()
            self.recording_active = False
    
    def record_audio(self, duration: float) -> Optional[np.ndarray]:
        try:
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels
            )
            sd.wait()
            return recording
        except Exception as e:
            print(f"Recording failed: {str(e)}")
            return None

    def speak(self, text: str) -> None:
        """Convert text to speech and play it"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Speech output error: {str(e)}")

    def test_audio(self) -> bool:
        """Test audio output"""
        try:
            self.speak("Testing audio output. Can you hear me?")
            return True
        except Exception as e:
            print(f"Audio test failed: {str(e)}")
            return False


