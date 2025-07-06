from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from clinic_data import APPOINTMENT_SLOTS, INSURANCE_PROVIDERS, DOCTORS, CLINIC_INFO

class ConversationHandler:
    def __init__(self, llm_model="gpt-4o"):
        self.llm = ChatOpenAI(model=llm_model)
        self.conversation_history = []
        self.patient_info = {
            "name": None,
            "insurance": None,
            "policy_number": None,
            "appointment_day": None,
            "appointment_time": None,
            "reason": None,
            "doctor_preference": None,
            "phone_number": None
        }
        self.current_intent = None
        self.conversation_state = "greeting"  # greeting, collecting_info, confirming, closing
        
        # Initialize system prompt
        self.system_prompt = self._create_system_prompt()
        
    def _create_system_prompt(self):
        """Create the system prompt with all clinic data embedded"""
        
        # Format appointment slots for the prompt
        appointment_text = ""
        for day, times in APPOINTMENT_SLOTS.items():
            appointment_text += f"- {day}: {', '.join(times)}\n"
            
        # Format insurance info
        insurance_text = ", ".join([ins for ins in INSURANCE_PROVIDERS if INSURANCE_PROVIDERS[ins]["accepted"]])
        
        # Format doctor info
        doctor_text = ""
        for name, info in DOCTORS.items():
            doctor_text += f"- Dr. {name} ({info['specialty']}): Available {', '.join(info['available_days'])}\n"
        
        # Format clinic hours
        hours_text = ""
        for day, hours in CLINIC_INFO["hours"].items():
            hours_text += f"- {day}: {hours}\n"
        
        return f"""
        You are an AI front desk assistant for {CLINIC_INFO["name"]}. Your job is to help patients with appointment scheduling, insurance verification, and answering questions about the clinic.

        IMPORTANT GUIDELINES:
        - Be professional, friendly, and empathetic
        - Ask only ONE question at a time
        - Never provide medical advice
        - Keep responses concise (under 3 sentences when possible)
        - If you don't understand something, politely ask for clarification
        - If the patient asks for something outside your capabilities, politely explain you can only help with appointments, insurance, and general clinic information
        - Always verify critical information by repeating it back to the patient

        CLINIC INFORMATION:
        - Name: {CLINIC_INFO["name"]}
        - Address: {CLINIC_INFO["address"]}
        - Phone: {CLINIC_INFO["phone"]}
        - Hours:\n{hours_text}
        - Services: {', '.join(CLINIC_INFO["services"])}
        - Website: {CLINIC_INFO["website"]}

        DOCTORS:
        {doctor_text}

        ACCEPTED INSURANCE:
        {insurance_text}

        AVAILABLE APPOINTMENT SLOTS:
        {appointment_text}

        CONVERSATION FLOW:
        1. Greet the patient and ask how you can help
        2. Identify if they need appointment scheduling, insurance verification, or general information
        3. For appointments: collect name, reason for visit, preferred day/time, and doctor preference (if any)
        4. For insurance: collect name, insurance provider, and policy number
        5. Verify the collected information
        6. Provide confirmation or answer
        7. Ask if there's anything else they need help with
        8. End the conversation politely

        Remember to maintain a natural, helpful conversation while efficiently collecting the necessary information.
        """
    
    def process_user_input(self, user_input):
        """Process user input and generate appropriate response"""
        
        # Add user input to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Determine intent if not already set
        if not self.current_intent and self.conversation_state == "greeting":
            self.current_intent = self._determine_intent(user_input)
            self.conversation_state = "collecting_info"
        
        # Update patient info based on input
        self._update_patient_info(user_input)
        
        # Check if all required patient info is present before confirming appointment
        if self.conversation_state == "collecting_info" and self._has_all_required_info():
            self.conversation_state = "confirming"
        
        # Generate response based on current state
        response = self._generate_response()
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Check if conversation is complete
        if "goodbye" in user_input.lower() or "thank you" in user_input.lower() or "bye" in user_input.lower():
            self.conversation_state = "closing"
        
        return response
    
    def _determine_intent(self, user_input):
        """Determine the user's intent from their input"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are analyzing a patient's request to a medical clinic. Categorize their intent as one of: 'appointment', 'insurance', or 'info'. Respond with just that single word."),
            ("human", user_input)
        ])
        
        intent_chain = prompt | self.llm
        intent = intent_chain.invoke({}).strip().lower()
        
        # Validate intent
        if intent not in ["appointment", "insurance", "info"]:
            intent = "info"  # Default to info if unclear
            
        return intent
    
    def _update_patient_info(self, user_input):
        """Extract and update patient information from user input"""
        # This would be more sophisticated in a real implementation
        # For now, we'll use a simple LLM-based extraction
        
        if self.current_intent == "appointment":
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
                Extract the following information from the patient's message if present:
                - Patient name
                - Appointment day
                - Appointment time
                - Reason for visit
                - Doctor preference
                
                Available days: {', '.join(APPOINTMENT_SLOTS.keys())}
                Available doctors: {', '.join(['Dr. ' + name for name in DOCTORS.keys()])}
                
                Return a JSON object with these fields. If information is not present, use null.
                Example: {{"name": "John Smith", "day": "Monday", "time": "10:00 AM", "reason": "checkup", "doctor": "Smith"}}
                Only return the JSON, nothing else.
                """),
                ("human", user_input)
            ])
            
            extraction_chain = prompt | self.llm
            try:
                import json
                result = extraction_chain.invoke({})
                extracted_info = json.loads(result)
                
                if extracted_info.get("name"):
                    self.patient_info["name"] = extracted_info["name"]
                if extracted_info.get("day"):
                    self.patient_info["appointment_day"] = extracted_info["day"]
                if extracted_info.get("time"):
                    self.patient_info["appointment_time"] = extracted_info["time"]
                if extracted_info.get("reason"):
                    self.patient_info["reason"] = extracted_info["reason"]
                if extracted_info.get("doctor"):
                    # Remove "Dr. " if present
                    doctor = extracted_info["doctor"]
                    if doctor.startswith("Dr. "):
                        doctor = doctor[4:]
                    self.patient_info["doctor_preference"] = doctor
            except:
                # If JSON parsing fails, continue without extraction
                pass
                
        elif self.current_intent == "insurance":
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""
                Extract the following information from the patient's message if present:
                - Patient name
                - Insurance provider
                - Policy number
                
                Available insurance providers: {', '.join(INSURANCE_PROVIDERS.keys())}
                
                Return a JSON object with these fields. If information is not present, use null.
                Example: {{"name": "John Smith", "insurance": "BlueCross", "policy_number": "ABC123456"}}
                Only return the JSON, nothing else.
                """),
                ("human", user_input)
            ])
            
            extraction_chain = prompt | self.llm
            try:
                import json
                result = extraction_chain.invoke({})
                extracted_info = json.loads(result)
                
                if extracted_info.get("name"):
                    self.patient_info["name"] = extracted_info["name"]
                if extracted_info.get("insurance"):
                    self.patient_info["insurance"] = extracted_info["insurance"]
                if extracted_info.get("policy_number"):
                    self.patient_info["policy_number"] = extracted_info["policy_number"]
            except:
                # If JSON parsing fails, continue without extraction
                pass
    
    def _has_all_required_info(self):
        """Check if we have all required information based on intent"""
        if self.current_intent == "appointment":
            return (
                self.patient_info["name"] and 
                self.patient_info["appointment_day"] and 
                self.patient_info["appointment_time"] and 
                self.patient_info["reason"]
            )
        elif self.current_intent == "insurance":
            return (
                self.patient_info["name"] and 
                self.patient_info["insurance"] and 
                self.patient_info["policy_number"]
            )
        return True  # For general info, no specific requirements
    
    def _generate_response(self):
        """Generate appropriate response based on conversation state"""
        
        # Create prompt with conversation history and current state
        messages = [("system", self.system_prompt)]
        
        # Add conversation history (last 5 exchanges to keep context manageable)
        history_to_include = self.conversation_history[-10:] if len(self.conversation_history) > 10 else self.conversation_history
        for message in history_to_include:
            if message["role"] == "user":
                messages.append(("human", message["content"]))
            else:
                messages.append(("assistant", message["content"]))
                
        # Add current state information to help guide the response
        state_info = f"""
        Current conversation state: {self.conversation_state}
        Current patient intent: {self.current_intent}
        
        Patient information collected so far:
        - Name: {self.patient_info['name']}
        - Insurance: {self.patient_info['insurance']}
        - Policy Number: {self.patient_info['policy_number']}
        - Appointment Day: {self.patient_info['appointment_day']}
        - Appointment Time: {self.patient_info['appointment_time']}
        - Reason for Visit: {self.patient_info['reason']}
        - Doctor Preference: {self.patient_info['doctor_preference']}
        
        Based on this information:
        
        1. If this is a greeting, welcome the patient and ask how you can help.
        
        2. If collecting information:
           - For appointments: If any required field is missing (name, day, time, reason), ask for it.
           - For insurance: If any required field is missing (name, insurance provider, policy number), ask for it.
           - For general info: Answer their question based on clinic information.
        
        3. If confirming:
           - For appointments: Confirm the appointment details and check if the slot is available.
           - For insurance: Verify if their insurance is accepted and confirm the details.
        
        4. If closing: Thank them for calling and wish them a good day.
        
        Remember to ask only ONE question at a time and keep responses concise and professional.
        """
        
        messages.append(("system", state_info))
        
        # Generate response
        prompt = ChatPromptTemplate.from_messages(messages)
        response_chain = prompt | self.llm
        response = response_chain.invoke({})
        
        # If confirming appointment, check if slot is available
        if self.conversation_state == "confirming" and self.current_intent == "appointment":
            day = self.patient_info["appointment_day"]
            time = self.patient_info["appointment_time"]
            
            # Check if slot is available
            if day in APPOINTMENT_SLOTS and time in APPOINTMENT_SLOTS[day]:
                # Slot is available, update response to confirm
                response += f"\n\nYour appointment has been confirmed for {day} at {time}."
                if self.patient_info["doctor_preference"]:
                    doctor = self.patient_info["doctor_preference"]
                    if doctor in DOCTORS and day in DOCTORS[doctor]["available_days"]:
                        response += f" with Dr. {doctor}."
                    else:
                        response += f" However, Dr. {doctor} is not available on {day}. Would you like to schedule with another doctor or choose a different day?"
            else:
                # Slot is not available
                response += f"\n\nI'm sorry, but the requested time slot ({time} on {day}) is not available. Would you like to choose another time or day?"
        
        # If confirming insurance, check if insurance is accepted
        if self.conversation_state == "confirming" and self.current_intent == "insurance":
            insurance = self.patient_info["insurance"]
            
            if insurance in INSURANCE_PROVIDERS and INSURANCE_PROVIDERS[insurance]["accepted"]:
                coverage = ", ".join(INSURANCE_PROVIDERS[insurance]["coverage_types"])
                response += f"\n\nI've verified that we accept {insurance} insurance. Your coverage includes: {coverage}."
            else:
                response += f"\n\nI'm sorry, but we don't currently accept {insurance} insurance. Would you like information about our self-pay options or other accepted insurance plans?"
        
        return response

    def get_greeting(self):
        """Return an initial greeting to start the conversation"""
        return f"Hello! Thank you for calling {CLINIC_INFO['name']}. I'm an AI assistant. How can I help you today?"

