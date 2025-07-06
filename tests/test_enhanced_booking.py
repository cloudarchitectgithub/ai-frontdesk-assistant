#!/usr/bin/env python3
"""
Test script to verify the enhanced information gathering system
"""

from simple_enhanced_assistant import SimpleEnhancedAssistant

def test_enhanced_booking():
    """Test the enhanced appointment booking with comprehensive information gathering"""
    assistant = SimpleEnhancedAssistant()
    
    print("=== TESTING ENHANCED APPOINTMENT BOOKING ===\n")
    
    # Test the complete enhanced flow
    test_conversation = [
        ("I need to book an appointment", "Initial request"),
        ("monday", "Day selection"),
        ("2 pm", "Time selection"),
        ("I have back pain", "Reason for visit"),
        ("dr. smith", "Doctor preference"),
        ("michael knight", "Name"),
        ("january 15, 1990", "Date of birth"),
        ("phone", "Contact preference"),
        ("407-123-4567", "Phone number"),
        ("yes", "Insurance verification"),
        ("blue cross blue shield", "Insurance provider"),
        ("ABC123456789", "Policy number")
    ]
    
    for i, (user_input, step_description) in enumerate(test_conversation, 1):
        print(f"{i}. {step_description}: '{user_input}'")
        response = assistant.process_input(user_input)
        print(f"   AI: {response}")
        print(f"   Booking step: {assistant.booking_step}")
        print()
    
    print("=== FINAL STATE ===")
    print(f"Patient: {assistant.patient_name}")
    print(f"DOB: {assistant.date_of_birth}")
    print(f"Phone: {assistant.phone}")
    print(f"Email: {assistant.email}")
    print(f"Date: {assistant.appointment_date}")
    print(f"Time: {assistant.appointment_time}")
    print(f"Doctor: {assistant.doctor_preference}")
    print(f"Reason: {assistant.reason_for_visit}")
    print(f"Insurance: {assistant.insurance_provider}")
    print(f"Policy: {assistant.insurance_policy_number}")
    print(f"Booking complete: {assistant.booking_step is None}")

if __name__ == "__main__":
    test_enhanced_booking() 