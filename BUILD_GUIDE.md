# 🏥 AI Front Desk Assistant - Complete Build Guide

A comprehensive guide to building a voice enabled AI assistant for healthcare front desk operations using Python, OpenAI Whisper, and ElevenLabs.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [System Architecture](#system-architecture)
- [Step-by-Step Build Process](#step-by-step-build-process)
- [Configuration & Setup](#configuration--setup)
- [Testing & Deployment](#testing--deployment)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

## 🎯 Overview

This AI assistant handles:
- **Voice based appointment scheduling**
- **Insurance verification**
- **Clinic information queries**
- **Natural conversation flow**
- **Call recording and logging**

### Key Features
- 🎤 Real time speech to text using OpenAI Whisper
- 🔊 High quality text to speech with ElevenLabs (or macOS fallback)
- 🤖 Intelligent conversation management
- 📅 Appointment slot management
- 🏥 Healthcare specific domain knowledge
- 📊 Call recording and analytics

## 🔧 Prerequisites

### Required Software
- **Python 3.9+**
- **macOS 10.15+** (for audio device compatibility)
- **Git**

### Required API Keys
- **OpenAI API Key** (for GPT-4 and Whisper)
- **ElevenLabs API Key** (for premium voice synthesis)

### Hardware Requirements
- **MacBook Pro** (or compatible Mac with built in microphone)
- **Headphones/Speakers** for audio output
- **Stable internet connection**

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Speech-to-Text  │───▶│  Conversation   │
│   (Microphone)  │    │   (Whisper API)  │    │    Handler      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Output  │◀───│  Text-to-Speech  │◀───│   AI Response   │
│   (Speakers)    │    │  (ElevenLabs)    │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

1. **Voice Handler** (`voice_handler_simple.py`)
   - Audio capture and playback
   - Speech to text conversion
   - Text to speech synthesis
   - Call recording management

2. **Conversation Handler** (`simple_enhanced_assistant.py`)
   - Intent detection
   - State management
   - Appointment booking logic
   - Insurance verification

3. **Main Application** (`main.py`)
   - Orchestrates components
   - Manages conversation flow
   - Handles error recovery

4. **Configuration** (`config.py`)
   - Environment settings
   - Audio parameters
   - API configurations

## 🚀 Step by Step Build Process

### Step 1: Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-frontdesk-assistant-mac

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: API Key Configuration

Create a `.env` file in the project root:

```bash
# Create environment file
touch .env
```

Add your API keys to `.env`:

```env
# OpenAI API Key (required for GPT-4 and Whisper)
OPENAI_API_KEY=sk-your-openai-api-key-here

# ElevenLabs API Key (optional - for premium voice)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here
```

### Step 3: Audio Device Configuration

The system automatically detects MacBook Pro audio devices:

```python
# In voice_handler_simple.py
def get_mac_audio_devices():
    """Get Mac mic and speakers device IDs"""
    devices = sd.query_devices()
    mac_mic = None
    mac_speakers = None
    
    for i, device in enumerate(devices):
        if 'MacBook Pro Microphone' in device['name']:
            mac_mic = i
        if 'MacBook Pro Speakers' in device['name']:
            mac_speakers = i
    
    return mac_mic, mac_speakers
```

### Step 4: Configuration Setup

Modify `config.py` for your clinic:

```python
# Clinic Information
CLINIC_NAME = "Your Clinic Name"
CLINIC_PHONE = "(555) 123-4567"
CLINIC_ADDRESS = "123 Medical Center Dr, City, State 12345"
CLINIC_HOURS = "Monday through Friday, 8:00 AM to 5:00 PM"

# Voice Settings
USE_ELEVENLABS = False  # Set to True for production
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Jessica voice

# Audio Settings
SAMPLE_RATE = 16000
LISTENING_WINDOW = 5  # seconds
PAUSE_BETWEEN_RESPONSES = 1  # seconds
```

### Step 5: Customize Clinic Data

Update clinic-specific information in `simple_enhanced_assistant.py`:

```python
# Available appointment slots
self.available_slots = {
    'monday': ['9:00 AM', '10:30 AM', '2:00 PM', '3:30 PM'],
    'tuesday': ['9:15 AM', '10:00 AM', '1:15 PM', '3:30 PM'],
    'wednesday': ['8:30 AM', '11:00 AM', '2:30 PM', '4:00 PM'],
    'thursday': ['9:00 AM', '10:15 AM', '1:00 PM', '3:45 PM'],
    'friday': ['8:45 AM', '10:30 AM', '2:15 PM', '4:30 PM']
}

# Available doctors
self.available_doctors = {
    'dr. smith': 'Dr. Sarah Smith - Family Medicine',
    'dr. johnson': 'Dr. Michael Johnson - Internal Medicine',
    # Add your doctors here
}

# Insurance providers
self.insurance_providers = [
    'Blue Cross Blue Shield', 'Aetna', 'Cigna', 
    'UnitedHealthcare', 'Humana', 'Medicare', 'Medicaid'
    # Add your accepted insurance providers
]
```

### Step 6: Test Audio Setup

Run the audio test script:

```bash
python test_mac_audio.py
```

This will:
- Test microphone input
- Test speaker output
- Verify device detection
- Check audio quality

### Step 7: Run the Assistant

Start the AI assistant:

```bash
python main.py
```

Or use the provided script:

```bash
./run_assistant.sh
```

## ⚙️ Configuration & Setup

### Voice Mode Configuration

The system supports two voice modes:

#### Testing Mode (Free)
```python
# In config.py
USE_ELEVENLABS = False
```
- Uses macOS built in speech synthesis
- No API costs
- Good for development and testing

#### Production Mode (Premium)
```python
# In config.py
USE_ELEVENLABS = True
```
- Uses ElevenLabs for high quality voice
- Requires API credits
- Professional voice quality

### Audio Settings

```python
# Sample rate for audio processing
SAMPLE_RATE = 16000  # Hz

# Listening window duration
LISTENING_WINDOW = 5  # seconds

# Pause between AI responses
PAUSE_BETWEEN_RESPONSES = 1  # seconds
```

### Debug Settings

```python
# Enable debug output for time extraction
DEBUG_TIME_EXTRACTION = True

# Enable conversation logging
DEBUG = True
```

## 🧪 Testing & Deployment

### Testing Workflow

1. **Audio Test**
   ```bash
   python test_mac_audio.py
   ```

2. **Voice Handler Test**
   ```bash
   python test_voice.py
   ```

3. **Conversation Test**
   ```bash
   python test_enhanced_booking.py
   ```

4. **Full System Test**
   ```bash
   python main.py
   ```

### Test Scenarios

#### Appointment Booking
```
User: "Hi, I'd like to book an appointment"
AI: "Could I get your full name for our records?"
User: "John Smith"
AI: "Thank you, John Smith. How can I assist you today?"
User: "I need an appointment for next Wednesday"
AI: "I have available slots on Wednesday at 8:30 AM, 11:00 AM, and 4:00 PM..."
```

#### Insurance Verification
```
User: "Do you accept Blue Cross Blue Shield?"
AI: "Yes, we do accept Blue Cross Blue Shield. Your copay would be $25..."
```

#### Clinic Information
```
User: "What are your hours?"
AI: "Our clinic hours are Monday through Friday, 8:00 AM to 5:00 PM..."
```

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production configuration
   export USE_ELEVENLABS=true
   export DEBUG=false
   ```

2. **Service Configuration**
   ```bash
   # Create systemd service (Linux)
   sudo nano /etc/systemd/system/ai-assistant.service
   ```

3. **Monitoring Setup**
   ```bash
   # Enable logging
   mkdir -p logs
   chmod 755 logs
   ```

## 🔧 Troubleshooting

### Common Issues

#### Audio Device Not Found
```bash
# Check available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**Solution**: Update device IDs in `voice_handler_simple.py`

#### Speech Recognition Issues
```bash
# Test OpenAI API connection
python -c "import openai; print(openai.Model.list())"
```

**Solution**: Verify API key and internet connection

#### ElevenLabs Voice Issues
```bash
# Test ElevenLabs connection
python test_elevenlabs.py
```

**Solution**: Check API key and voice ID

### Debug Commands

```bash
# Test microphone
python mic_test.py

# Test speech recognition
python test_time_recognition.py

# Test conversation flow
python test_completed_appointment.py

# Check system health
python diagnostic_test.py
```

### Log Analysis

```bash
# View conversation logs
ls -la logs/

# Check recent conversations
tail -f logs/conversation_*.json

# Analyze call recordings
ls -la recordings/
```

## 🚀 Production Considerations

### Security

1. **API Key Management**
   ```bash
   # Use environment variables
   export OPENAI_API_KEY="your-key"
   export ELEVENLABS_API_KEY="your-key"
   ```

2. **Data Privacy**
   - Implement HIPAA compliance
   - Encrypt stored data
   - Regular data cleanup

3. **Access Control**
   - Restrict file permissions
   - Implement user authentication
   - Monitor access logs

### Performance

1. **Resource Optimization**
   ```python
   # Optimize audio settings
   SAMPLE_RATE = 16000  # Balance quality vs performance
   CHUNK_SIZE = 1024    # Audio processing chunks
   ```

2. **Memory Management**
   ```python
   # Clear conversation history periodically
   if len(self.conversation_history) > 100:
       self.conversation_history = self.conversation_history[-50:]
   ```

3. **Error Recovery**
   ```python
   # Implement retry logic
   def speech_to_text_with_retry(self, max_retries=3):
       for attempt in range(max_retries):
           try:
               return self.speech_to_text()
           except Exception as e:
               if attempt == max_retries - 1:
                   raise e
               time.sleep(1)
   ```

### Scalability

1. **Load Balancing**
   - Deploy multiple instances
   - Use reverse proxy
   - Implement queue system

2. **Monitoring**
   ```python
   # Add health checks
   def health_check(self):
       return {
           "status": "healthy",
           "audio_devices": self.check_audio_devices(),
           "api_connections": self.check_api_connections(),
           "memory_usage": self.get_memory_usage()
       }
   ```

3. **Backup & Recovery**
   ```bash
   # Backup configuration
   cp config.py config.py.backup
   
   # Backup conversation logs
   tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
   ```

## 📚 Additional Resources

### Documentation
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [ElevenLabs API](https://elevenlabs.io/docs/api-reference)
- [SoundDevice Documentation](https://python-sounddevice.readthedocs.io/)

### Support
- Check the `logs/` directory for error details
- Review `recordings/` for audio quality issues
- Use debug mode for detailed troubleshooting

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 🎉 Congratulations!

You've successfully built a professional AI front desk assistant! The system is now ready to handle patient calls, schedule appointments, and provide clinic information through natural voice conversations.

### Next Steps
1. **Customize** the clinic information for your specific needs
2. **Test** thoroughly with real scenarios
3. **Deploy** to production environment
4. **Monitor** performance and user feedback
5. **Iterate** and improve based on usage patterns

For questions or support, please refer to the troubleshooting section or create an issue in the repository. 
