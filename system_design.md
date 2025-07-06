## Architecture Overview

The AI Front Desk Assistant uses a modular architecture with four primary components:

1. **Voice Handler (Speech-to-Text & Text-to-Speech)**
   - Captures audio input from patients
   - Converts speech to text using Whisper
   - Converts AI responses to speech using pyttsx3
   - Manages audio device selection and configuration

2. **Conversation Handler**
   - Maintains conversation state and patient information
   - Extracts relevant information from user inputs
   - Determines user intent (appointment, insurance, general info)
   - Generates appropriate responses based on context

3. **LLM Integration**
   - Processes natural language using OpenAI's GPT models
   - Extracts structured data from unstructured patient inputs
   - Generates contextually appropriate responses
   - Maintains conversation coherence

4. **Data Management**
   - Stores clinic information (hours, services, doctors)
   - Manages appointment slots and availability
   - Records patient information and appointment details
   - Logs conversations for quality assurance

### Component Interaction Flow:
1. Patient speaks → Voice Handler captures and converts to text
2. Text sent to Conversation Handler to update state and extract info
3. Conversation Handler uses LLM to generate appropriate response
4. Response sent to Voice Handler for text-to-speech conversion
5. Audio response played back to patient

## Tech Stack & Tools

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Speech-to-Text | OpenAI Whisper | High accuracy across accents and medical terminology; offline capability |
| Text-to-Speech | pyttsx3 | Cross-platform, offline capability, no API costs |
| LLM | OpenAI GPT-4 | Best performance for complex medical conversations and entity extraction |
| Conversation Management | Custom Python classes | Tailored to healthcare domain requirements |
| Audio Processing | sounddevice, soundfile | Reliable cross-platform audio capture |
| Development | Python, FastAPI | Rapid prototyping, extensive library support |

**Alternative Technologies Considered:**
- ElevenLabs for TTS: Better voice quality but requires API calls and costs
- Azure Speech Services: Good integration but less accuracy with medical terms
- Claude or Llama for LLM: Considered for cost but GPT-4 had better performance

## Prompt Engineering

The system uses a multi-layered prompting strategy:

1. **System Prompt** - Establishes the assistant's identity and constraints:
```
You are an AI front desk assistant for {CLINIC_INFO["name"]}. Your job is to help patients with appointment scheduling, insurance verification, and answering questions about the clinic.

IMPORTANT GUIDELINES:
- Be professional, friendly, and empathetic
- Ask only ONE question at a time
- Never provide medical advice
- Keep responses concise (under 3 sentences when possible)
```

2. **Intent Classification** - Determines what the patient needs:
```
You are analyzing a patient's request to a medical clinic. Categorize their intent as one of: 'appointment', 'insurance', or 'info'. Respond with just that single word.
```

3. **Entity Extraction** - Structured JSON extraction for appointments:
```
Extract the following information from the patient's message if present:
- Patient name
- Appointment day
- Appointment time
- Reason for visit
- Doctor preference

Return a JSON object with these fields. If information is not present, use null.
```

4. **State-Based Prompting** - Contextual prompts based on conversation state:
```
You are in the {self.conversation_state} phase of a conversation with a patient.
The patient's current information is: {self.patient_info}
Your next task is to {specific_instruction_based_on_state}
```

**Challenges & Solutions:**
- **Challenge**: LLM generating multiple questions at once
  **Solution**: Added explicit "Ask only ONE question at a time" instruction and state tracking

- **Challenge**: Inconsistent entity extraction
  **Solution**: Implemented structured JSON extraction with clear field definitions

- **Challenge**: Handling emergency situations
  **Solution**: Added keyword detection for emergency terms with immediate redirection

## Assumptions & Limitations

### Assumptions
- Single-speaker environment with minimal background noise
- Patient speaks English with no heavy accent
- Dates provided in standard format (day of week or MM/DD)
- Patient has basic knowledge of medical appointment processes
- Conversations follow typical appointment/insurance inquiry patterns

### Current Limitations
- Limited to pre-defined appointment slots (no real calendar integration)
- No authentication or verification of patient identity
- No integration with electronic health records
- Limited handling of complex insurance scenarios
- No multi-language support
- No handling of concurrent conversations

### Future Improvements
1. **Integration Opportunities**:
   - Connect to real EHR/EMR systems (Epic, Cerner)
   - Integrate with calendar APIs (Google Calendar, Microsoft Outlook)
   - Add insurance verification API connections
   - Implement SMS/email confirmation system

2. **Technical Enhancements**:
   - Implement HIPAA-compliant data storage
   - Add voice biometrics for patient identification
   - Support multiple languages and dialects
   - Develop web interface for staff to monitor conversations
   - Implement more sophisticated error recovery

3. **Scalability Considerations**:
   - Deploy as cloud service with load balancing
   - Implement conversation queuing for high-volume periods
   - Add analytics dashboard for call patterns and common issues
   - Develop staff escalation protocol for complex cases