"""
Enhanced appointment handling logic for the front desk assistant
"""

from typing import List, Optional, Dict, Any

class AppointmentHandler:
    def __init__(self):
        self.available_slots = {
            "monday": ["9:00 AM", "10:30 AM", "2:00 PM", "3:30 PM"],
            "tuesday": ["9:15 AM", "10:00 AM", "1:15 PM", "3:30 PM"],
            "wednesday": ["8:30 AM", "11:00 AM", "2:30 PM", "4:00 PM"],
            "thursday": ["9:00 AM", "10:15 AM", "1:00 PM", "3:45 PM"],
            "friday": ["8:45 AM", "10:30 AM", "2:15 PM", "4:30 PM"]
        }
        self.conversation_state = {}
    
    def process_appointment_request(self, user_input: str, conversation_history: list) -> str:
        """Process appointment booking with improved logic"""
        user_input_lower = user_input.lower().strip()
        
        # Check if user is selecting a time slot
        if self._is_time_selection(user_input_lower):
            return self._handle_time_selection(user_input_lower, conversation_history)
        
        # Check if user is selecting a day
        if self._is_day_selection(user_input_lower):
            return self._handle_day_selection(user_input_lower)
        
        # Initial appointment request
        if "appointment" in user_input_lower or "book" in user_input_lower or "schedule" in user_input_lower:
            return "I'd be happy to help you schedule an appointment. What day would work best for you? We're open Monday through Friday."
        
        return "I'm not sure I understood. Could you please clarify what you need help with?"
    
    def _is_time_selection(self, user_input: str) -> bool:
        """Check if user input contains time selection"""
        time_indicators = ["am", "pm", ":", "o'clock", "morning", "afternoon"]
        return any(indicator in user_input for indicator in time_indicators)
    
    def _is_day_selection(self, user_input: str) -> bool:
        """Check if user input contains day selection"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        return any(day in user_input for day in days)
    
    def _handle_time_selection(self, user_input: str, conversation_history: list) -> str:
        """Handle time slot selection with better matching"""
        # Extract the selected day from conversation history
        selected_day = self._extract_day_from_history(conversation_history)
        if not selected_day:
            return "I need to know which day you'd like to book. What day works best for you?"
        
        # Parse the time from user input
        selected_time = self._parse_time_input(user_input)
        available_slots = self.available_slots.get(selected_day, [])
        
        # Find matching time slot
        matching_slot = self._find_matching_time_slot(selected_time, available_slots)
        
        if matching_slot:
            return f"Perfect! I'll book your appointment for {selected_day.title()} at {matching_slot}. May I ask what brings you in today?"
        else:
            available_times = ", ".join(available_slots)
            return f"I don't have {selected_time} available on {selected_day.title()}. The available times are: {available_times}. Which would you prefer?"
    
    def _handle_day_selection(self, user_input: str) -> str:
        """Handle day selection"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        selected_day = next((day for day in days if day in user_input), None)
        
        if selected_day and selected_day in self.available_slots:
            available_times = ", ".join(self.available_slots[selected_day])
            return f"For {selected_day.title()}, I have these times available: {available_times}. Which time works best for you?"
        else:
            return "I'm sorry, we're only open Monday through Friday. Which day would work best for you?"
    
    def _parse_time_input(self, user_input: str) -> str:
        """Parse time from user input"""
        # Handle common time formats
        if "10" in user_input and ("am" in user_input or "a.m" in user_input or "morning" in user_input):
            return "10:00 AM"
        elif "9:15" in user_input or "9 15" in user_input or "nine fifteen" in user_input:
            return "9:15 AM"
        elif "1:15" in user_input or "1 15" in user_input or "one fifteen" in user_input:
            return "1:15 PM"
        elif "3:30" in user_input or "3 30" in user_input or "three thirty" in user_input:
            return "3:30 PM"
        
        return user_input  # Return as-is if no pattern matched
    
    def _find_matching_time_slot(self, selected_time: str, available_slots: list) -> Optional[str]:
        """Find the best matching time slot"""
        selected_time_lower = selected_time.lower()
        
        for slot in available_slots:
            slot_lower = slot.lower()
            # Exact match
            if selected_time_lower == slot_lower:
                return slot
            # Partial match (e.g., "10" matches "10:00 AM")
            if selected_time_lower in slot_lower or slot_lower in selected_time_lower:
                return slot
        
        return None
    
    def _extract_day_from_history(self, conversation_history: list) -> Optional[str]:
        """Extract the selected day from conversation history"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        
        # Look through recent conversation for day selection
        for message in reversed(conversation_history):
            if isinstance(message, dict) and "content" in message:
                message_lower = message["content"].lower()
            else:
                message_lower = str(message).lower()
                
            for day in days:
                if day in message_lower:
                    return day
        
        return None