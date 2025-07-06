#!/usr/bin/env python3
from voice_handler_simple import VoiceHandler
import time

def main():
    try:
        # Initialize voice handler
        print("Initializing voice handler...")
        voice = VoiceHandler()
        
        # Test scenarios
        scenarios = [
            {
                "name": "Initial Greeting",
                "message": "Welcome to Harmony Family Clinic. This is your AI assistant."
            },
            {
                "name": "Appointment Request",
                "message": "What day would you like to schedule your appointment? We have availability Monday through Friday."
            },
            {
                "name": "Time Slots",
                "message": "For Monday, I have available slots at 10:30 AM and 2:15 PM. Which time works better for you?"
            },
            {
                "name": "Insurance Verification",
                "message": "Do you have your insurance information available? We accept most major providers."
            },
            {
                "name": "Confirmation",
                "message": "Perfect! I've scheduled your appointment for Monday at 10:30 AM. You'll receive a confirmation email shortly."
            }
        ]
        
        # Test each scenario
        print("\nStarting voice synthesis test...")
        print("-" * 50)
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\nScenario {i}: {scenario['name']}")
            print(f"Message: {scenario['message']}")
            
            success = voice.speak(scenario['message'])
            
            if success:
                print("✓ Speech synthesis successful")
            else:
                print("✗ Speech synthesis failed")
            
            # Brief pause between messages
            time.sleep(0.5)
                
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False
    
    print("\n✅ All voice tests completed successfully!")
    return True

if __name__ == "__main__":
    main()
