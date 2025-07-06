import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class LLMHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """
        You are an AI front desk assistant for Wellness Medical Center. Your role is to:
        1. Help patients schedule appointments
        2. Verify insurance information
        3. Answer basic clinic questions
        
        Rules:
        - Always be polite and professional
        - Ask one question at a time
        - Don't provide medical advice
        - For appointment scheduling, collect: patient name, preferred date/time, reason for visit
        - For insurance verification, collect: patient name, insurance provider, policy number
        - Confirm details before finalizing
        - If unsure, ask for clarification
        - Keep responses concise
        """
        
    def generate_response(self, user_input, conversation_history=[]):
        """Generate a response using the OpenAI API"""
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_input})
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm sorry, I'm having trouble processing your request. Could you please try again?"
