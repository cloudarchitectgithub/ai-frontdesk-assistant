from simple_enhanced_assistant import SimpleEnhancedAssistant
from voice_handler_simple import VoiceHandler
import json
import os
import time
from datetime import datetime
from config import USE_ELEVENLABS, LISTENING_WINDOW, PAUSE_BETWEEN_RESPONSES

def main():
    """Main function to run the AI front desk assistant"""
    print("\n=== AI FRONT-DESK ASSISTANT FOR HEALTHCARE CLINIC ===\n")
    
    try:
        # Setup voice handler with Mac mic and speakers
        # Use configuration to determine ElevenLabs usage
        voice_handler = VoiceHandler(use_elevenlabs=USE_ELEVENLABS)
        
        if USE_ELEVENLABS:
            print("Using ElevenLabs for text-to-speech (production mode)")
        else:
            print("Using macOS speech synthesis (testing mode - no credits used)")
        
        # Initialize the enhanced front desk assistant
        assistant = SimpleEnhancedAssistant()
        
        print("\nInitialization complete. Starting conversation...\n")
        
        # Start call recording
        voice_handler.start_call_recording()
        
        # Initial greeting
        initial_response = "Thank you for calling Harmony Family Clinic. This is the virtual assistant speaking. How may I assist you today?"
        print(f"AI: {initial_response}")
        voice_handler.text_to_speech(initial_response)
        
        # Conversation loop
        conversation_count = 0
        max_conversations = 50  # Prevent infinite loops
        
        while conversation_count < max_conversations:
            conversation_count += 1
            
            # Get user input - use configured listening window
            print(f"\nListening... ({LISTENING_WINDOW} second window)")
            user_input = voice_handler.speech_to_text(LISTENING_WINDOW)
            
            if not user_input:
                print("No input detected, continuing...")
                continue
            
            print(f"Patient: {user_input}")
            
            # Check for goodbye intent directly first
            if assistant.detect_intent(user_input) == 'goodbye':
                print("\nUser indicated end of conversation.")
                final_response = assistant.process_input(user_input)  # Use enhanced goodbye
                print(f"AI: {final_response}")
                voice_handler.text_to_speech(final_response)
                break
            
            # Process user input
            ai_response = assistant.process_input(user_input)
            print(f"AI: {ai_response}")
            
            # Convert response to speech
            voice_handler.text_to_speech(ai_response)
            
            # Add configured pause before listening again
            print(f"Pausing {PAUSE_BETWEEN_RESPONSES} second before listening...")
            time.sleep(PAUSE_BETWEEN_RESPONSES)
            
            # Check for conversation end
            if any(phrase in ai_response.lower() for phrase in [
                'thank you for calling', 'thank you for choosing', 
                'have a wonderful day', 'have a nice day', 'goodbye'
            ]):
                print("\nConversation ended with goodbye message.")
                break
                
        if conversation_count >= max_conversations:
            print("\nMaximum conversation limit reached. Ending call.")
            final_response = assistant.process_input("goodbye")  # Use enhanced goodbye
            print(f"AI: {final_response}")
            voice_handler.text_to_speech(final_response)
            
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        print("Please ensure all required files are present:")
        print("- simple_enhanced_assistant.py")
        print("- voice_handler_simple.py")
        print("- config.py")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting gracefully...")
        # Stop any active recording
        if 'voice_handler' in locals() and hasattr(voice_handler, 'stop_current_recording'):
            voice_handler.stop_current_recording()
        
        # Say goodbye
        print("\nThank you for using the AI Front Desk Assistant. Goodbye!")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        print("Ending call gracefully...")
    finally:
        # Stop call recording and save the complete conversation
        if 'voice_handler' in locals():
            voice_handler.stop_call_recording()

def save_conversation_log(assistant):
    """Save the conversation log to a file"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/conversation_{timestamp}.json"
    
    # Prepare log data
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "patient_info": assistant.state.to_dict(),
        "conversation_history": assistant.state.conversation_history
    }
    
    # Save to file
    with open(filename, "w") as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\nConversation log saved to {filename}")

if __name__ == "__main__":
    main()
