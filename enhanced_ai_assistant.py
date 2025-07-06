"""
Simple Enhanced Front-Desk Assistant
Drop-in replacement for your existing assistant
"""

import re
import json
import time
from typing import Dict, List, Optional, Any
from appointment_handler import AppointmentHandler
from datetime import datetime
import os

class AppointmentError(Exception):
    pass

class SimpleEnhancedAssistant:
    def __init__(self):
        # Patient information
        self.patient_name = None
        self.phone = None
        self.appointment_date = None
        self.appointment_time = None
        self.reason_for_visit = None
        self.context = "greeting"
        
        # Available slots
        self.available_slots = {
            'monday': ['9:00 AM', '10:30 AM', '2:00 PM', '3:30 PM'],
            'tuesday': ['9:15 AM', '10:00 AM', '1:15 PM', '3:30 PM'],
            'wednesday': ['8:30 AM', '11:00 AM', '2:30 PM', '4:00 PM'],
            'thursday': ['9:00 AM', '10:15 AM', '1:00 PM', '3:45 PM'],
            'friday': ['8:45 AM', '10:30 AM', '2:15 PM', '4:30 PM']
        }
        
        # Insurance providers
        self.insurance_providers = [
            'Blue Cross Blue Shield', 'BCBS', 'Aetna', 'Cigna', 
            'UnitedHealthcare', 'United', 'Humana', 'Kaiser', 
            'Anthem', 'Medicare', 'Medicaid'
        ]
        
        # Add conversation history tracking
        self.conversation_history = []
        
        # Initialize the appointment handler
        self.appointment_handler = AppointmentHandler()
        
        # Appointment directory
        self.appointments_dir = "appointments"
        os.makedirs(self.appointments_dir, exist_ok=True)

    def process_input(self, user_input):
        """Main processing function - drop-in replacement"""
        if not user_input or not user_input.strip():
            return "I'm sorry, I didn't hear anything. Could you please repeat that?"
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Fix common speech errors
        cleaned_input = self.fix_speech_errors(user_input)
        intent = self.detect_intent(cleaned_input)
        
        # Handle different intents
        if intent == 'insurance':
            response = self.handle_insurance(cleaned_input)
        elif intent == 'hours':
            response = "Our clinic hours are Monday through Friday, 8:00 AM to 5:00 PM. We're closed on weekends. Would you like to schedule an appointment?"
        elif intent == 'location':
            response = "We're located at 123 Health Street, Orlando, FL 32801 in the Medical Plaza building with plenty of parking. Can I help you schedule a visit?"
        elif intent == 'cost':
            response = "Our fees vary by service and insurance coverage. We accept most insurance plans and offer competitive self-pay rates. Would you like to schedule an appointment to discuss your needs?"
        elif intent == 'goodbye':
            response = "Thank you for calling Harmony Family Clinic. Have a wonderful day!"
        elif intent == 'appointment':
            # Use the enhanced appointment handler
            response = self.appointment_handler.process_appointment_request(cleaned_input, self.conversation_history)
            
            # Update appointment information if it was set by the handler
            self._update_appointment_info_from_conversation()
        else:
            response = self.handle_appointment_flow(cleaned_input)
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _update_appointment_info_from_conversation(self):
        """Update appointment information based on conversation history"""
        # Extract day
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        for day in days:
            day_pattern = re.compile(r'appointment for ' + day.title(), re.IGNORECASE)
            for message in reversed(self.conversation_history):
                if "content" in message and day_pattern.search(message["content"]):
                    self.appointment_date = day
                    break
        
        # Extract time
        time_pattern = re.compile(r'appointment for \w+ at (\d{1,2}:\d{2} [AP]M)', re.IGNORECASE)
        for message in reversed(self.conversation_history):
            if "content" in message:
                time_match = time_pattern.search(message["content"])
                if time_match:
                    self.appointment_time = time_match.group(1)
                    break

    def fix_speech_errors(self, text):
        """Fix common speech-to-text errors"""
        text = text.strip()
        
        # Time corrections
        corrections = {
            'turn am': '10:00 AM',
            'turn AM': '10:00 AM',
            '10 am': '10:00 AM',
            '10am': '10:00 AM',
            '9.15': '9:15 AM',
            '9:15': '9:15 AM',
            '1.15': '1:15 PM',
            '1:15': '1:15 PM',
            '3.30': '3:30 PM',
            '3:30': '3:30 PM',
            'nine fifteen': '9:15 AM',
            'ten am': '10:00 AM',
            'one fifteen': '1:15 PM',
            'three thirty': '3:30 PM'
        }
        
        text_lower = text.lower()
        for error, fix in corrections.items():
            if error in text_lower:
                return text.replace(error, fix)
        
        return text

    def extract_day(self, text):
        """Extract day from text"""
        text = text.lower()
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        
        for day in days:
            if day in text or day[:3] in text:
                return day
        return None

    def extract_time(self, text):
        """Extract time with better error handling"""
        text = self.fix_speech_errors(text)
        
        # Normalize the text for better matching
        text = text.lower().replace('.', ':')
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)',
            r'(\d{1,2})\s*(am|pm)',
            r'(\d{1,2}):(\d{2})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                # Format the time consistently
                if len(match.groups()) == 3:  # HH:MM AM/PM format
                    hour, minute, ampm = match.groups()
                    return f"{hour}:{minute} {ampm.upper()}"
                elif len(match.groups()) == 2:
                    if ':' in match.group(0):  # HH:MM format
                        hour, minute = match.groups()
                        # Assume PM for afternoon hours
                        ampm = "PM" if int(hour) >= 12 and int(hour) < 24 else "AM"
                        return f"{hour}:{minute} {ampm}"
                    else:  # HH AM/PM format
                        hour, ampm = match.groups()
                        return f"{hour}:00 {ampm.upper()}"
        
        # Check for simple hour mentions (e.g., "11 a.m.")
        hour_pattern = r'(\d{1,2})(?:\s*)(a\.m\.|am|a\.m|p\.m\.|pm|p\.m)'
        hour_match = re.search(hour_pattern, text)
        if hour_match:
            hour = hour_match.group(1)
            am_pm = 'AM' if any(x in hour_match.group(2).lower() for x in ['a', 'am']) else 'PM'
            return f"{hour}:00 {am_pm}"
        
        return None

    def extract_phone(self, text):
        """Extract phone number"""
        # Remove words
        numbers_only = re.sub(r'[^\d\s]', '', text)
        digits = re.findall(r'\d', numbers_only)
        
        if len(digits) >= 10:
            phone_str = ''.join(digits[:10])
            return f"({phone_str[:3]}) {phone_str[3:6]}-{phone_str[6:]}"
        
        return None

    def detect_intent(self, text):
        """Detect what the user wants"""
        text = text.lower()
        
        # Expanded goodbye phrases
        goodbye_phrases = [
            'goodbye', 'bye', 'thank you', 'thanks', 
            'that\'s it', 'i\'m finished', 'i\'m done', 'no that\'s all',
            'that\'s all', 'end call', 'hang up', 'finished', 'done',
            'no more questions', 'nothing else'
        ]
        
        # Check for goodbye intent first
        for phrase in goodbye_phrases:
            if phrase in text:
                return 'goodbye'
        
        # Then check other intents
        if any(word in text for word in ['appointment', 'book', 'schedule', 'visit']):
            return 'appointment'
        elif any(word in text for word in ['insurance', 'coverage', 'plan', 'blue cross', 'aetna']):
            return 'insurance'
        elif any(word in text for word in ['hours', 'open', 'time', 'when']):
            return 'hours'
        elif any(word in text for word in ['where', 'location', 'address']):
            return 'location'
        elif any(word in text for word in ['cost', 'price', 'fee', 'charge']):
            return 'cost'
        
        return 'general'

    def handle_insurance(self, text):
        """Handle insurance questions"""
        text_lower = text.lower()
        
        # Check for specific insurance mentioned
        for insurance in self.insurance_providers:
            if insurance.lower() in text_lower:
                return f"Yes, we do accept {insurance}. Most of their plans are in-network with our providers. Would you like me to verify your specific coverage when you come in?"
        
        # General insurance question
        return "We accept most major insurance plans including Blue Cross Blue Shield, Aetna, Cigna, UnitedHealthcare, Humana, and others. Which insurance provider do you have?"

    def handle_appointment_flow(self, user_input):
        """Handle appointment booking flow"""
        
        # Initial appointment request
        if any(word in user_input.lower() for word in ['appointment', 'book', 'schedule']) and not self.appointment_date:
            self.context = "scheduling"
            return "I'd be happy to help you schedule an appointment. What day would work best for you? We're open Monday through Friday."
        
        # Day selection
        day = self.extract_day(user_input)
        if day and not self.appointment_date:
            self.appointment_date = day
            slots = self.available_slots.get(day, [])
            slots_text = ", ".join(slots)
            return f"For {day.title()}, I have these times available: {slots_text}. Which time works best for you?"
        
        # Time selection
        time = self.extract_time(user_input)
        if time and self.appointment_date and not self.appointment_time:
            # Check if time is available
            available_times = self.available_slots.get(self.appointment_date, [])
            
            # Normalize the extracted time and available times for comparison
            normalized_time = time.lower().replace('.', ':').replace(' ', '')
            
            for available_time in available_times:
                normalized_avail = available_time.lower().replace('.', ':').replace(' ', '')
                
                # Check for exact match or partial match
                if normalized_time == normalized_avail or normalized_time in normalized_avail:
                    self.appointment_time = available_time
                    return f"Perfect! I have you scheduled for {self.appointment_date.title()} at {available_time}. May I ask what brings you in today?"
        
            # If we get here, no match was found
            # Try to match just the hour part
            hour_match = re.search(r'(\d{1,2})', time)
            if hour_match:
                hour = hour_match.group(1)
                for available_time in available_times:
                    if hour in available_time.split(':')[0]:
                        self.appointment_time = available_time
                        return f"Perfect! I have you scheduled for {self.appointment_date.title()} at {available_time}. May I ask what brings you in today?"
        
            # Time not available
            slots_text = ", ".join(available_times)
            return f"I don't have {time} available on {self.appointment_date.title()}. The available times are: {slots_text}. Which works for you?"
        
        # Reason for visit
        if self.appointment_date and self.appointment_time and not self.reason_for_visit and not any(word in user_input.lower() for word in ['name', 'phone', 'email']):
            self.reason_for_visit = user_input.strip()
            return "Thank you for that information. Could I get your full name for our records?"
        
        # Name collection
        if ('name' in user_input.lower() or not self.patient_name) and self.appointment_time:
            # Extract name
            if 'name is' in user_input.lower():
                name_part = user_input.lower().split('name is')[1].strip()
                self.patient_name = name_part.title()
            elif 'i\'m' in user_input.lower():
                name_part = user_input.lower().split('i\'m')[1].strip()
                self.patient_name = name_part.title()
            else:
                # Assume the input is the name if we're asking for it
                self.patient_name = user_input.strip().title()
            
            return f"Thank you, {self.patient_name}. Would you like me to send a confirmation to your phone or email?"
        
        # Phone collection
        phone = self.extract_phone(user_input)
        if phone:
            self.phone = phone
            return f"Perfect! I'll send a confirmation to {phone}. Your appointment summary:\n\nPatient: {self.patient_name}\nDate: {self.appointment_date.title()}\nTime: {self.appointment_time}\nReason: {self.reason_for_visit}\n\nPlease arrive 15 minutes early. Is there anything else I can help you with?"
        
        # Default responses based on context
        if not self.appointment_date:
            return "What day would work best for your appointment? We have availability Monday through Friday."
        elif not self.appointment_time:
            slots = self.available_slots.get(self.appointment_date, [])
            slots_text = ", ".join(slots)
            return f"For {self.appointment_date.title()}, which time works best: {slots_text}?"
        
        # General helpful response
        return "I'm here to help with appointments, insurance questions, or any other information you need. How can I assist you?"
    
    def get_appointment_summary(self):
        """Return a formatted appointment summary"""
        if not self.appointment_date or not self.appointment_time:
            return "No appointment has been scheduled."
            
        summary = f"""
=== APPOINTMENT SUMMARY ===
Patient: {self.patient_name or 'Not provided'}
Date: {self.appointment_date.title()}
Time: {self.appointment_time}
Reason: {self.reason_for_visit or 'Not specified'}
Contact: {self.phone or 'Not provided'}

Please arrive 15 minutes early to complete paperwork.
Thank you for choosing Harmony Family Clinic!
"""
        return summary
        
    def to_dict(self):
        """Convert state to dictionary for saving"""
        return {
            "patient_name": self.patient_name,
            "phone": self.phone,
            "appointment_date": self.appointment_date,
            "appointment_time": self.appointment_time,
            "reason_for_visit": self.reason_for_visit,
            "context": self.context
        }
    
    def save_appointment(self, appointment_data: Dict[str, Any]) -> str:
        try:
            # Validate appointment data
            self._validate_appointment_data(appointment_data)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"appointment_{timestamp}.json"
            filepath = os.path.join(self.appointments_dir, filename)
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(appointment_data, f, indent=2)
            
            return filepath
            
        except Exception as e:
            raise AppointmentError(f"Failed to save appointment: {str(e)}")
    
    def _validate_appointment_data(self, data: Dict[str, Any]) -> None:
        required_fields = ["name", "day", "time"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")








