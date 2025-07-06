class AppointmentScheduler:
    def __init__(self):
        self.doctors = {
            "Dr. Smith": ["Monday", "Wednesday", "Friday"],
            "Dr. Johnson": ["Tuesday", "Thursday"]
        }
        self.available_slots = {
            "Monday": ["9:00 AM", "11:00 AM", "2:00 PM"],
            "Tuesday": ["10:00 AM", "3:00 PM"],
            # Add more days...
        }
        
    def check_availability(self, day, doctor=None):
        if doctor:
            if day not in self.doctors[doctor]:
                return None
        return self.available_slots.get(day, [])
        
    def book_appointment(self, patient_name, day, time, doctor=None, reason=""):
        # In a real system, this would update a database
        return f"Appointment confirmed for {patient_name} on {day} at {time}" + \
               (f" with {doctor}" if doctor else "") + \
               (f" for {reason}" if reason else "")