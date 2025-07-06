from typing import Dict, List, Optional

class Config:
    DEBUG: bool = False
    VOICE_ENABLED: bool = True
    
    # Audio settings
    AUDIO_SAMPLE_RATE: int = 44100
    AUDIO_CHANNELS: int = 1
    
    # OpenAI settings
    OPENAI_MODEL: str = "gpt-4"
    MAX_TOKENS: int = 150
    TEMPERATURE: float = 0.7
    
    # Appointment settings
    MIN_APPOINTMENT_DURATION: int = 30
    MAX_APPOINTMENTS_PER_DAY: int = 20
    BUSINESS_HOURS: Dict[str, Dict[str, str]] = {
        "Monday": {"start": "09:00", "end": "17:00"},
        "Tuesday": {"start": "09:00", "end": "17:00"},
        "Wednesday": {"start": "09:00", "end": "17:00"},
        "Thursday": {"start": "09:00", "end": "17:00"},
        "Friday": {"start": "09:00", "end": "17:00"}
    }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        errors = []
        # Add validation logic
        return errors

# Configuration for AI Front Desk Assistant

# Voice Settings
USE_ELEVENLABS = False  # Set to True for production, False for testing
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Jessica voice

# Audio Settings
SAMPLE_RATE = 16000
LISTENING_WINDOW = 5  # seconds
PAUSE_BETWEEN_RESPONSES = 1  # seconds

# Debug Settings
DEBUG_TIME_EXTRACTION = True  # Set to False to disable time extraction debug output

# Clinic Settings
CLINIC_NAME = "Harmony Family Clinic"
CLINIC_PHONE = "(407) 555-0123"
CLINIC_ADDRESS = "123 Health Street, Orlando, FL 32801"
CLINIC_HOURS = "Monday through Friday, 8:00 AM to 5:00 PM"