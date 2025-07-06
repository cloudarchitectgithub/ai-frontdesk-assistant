# Configuration for the AI Front Desk Assistant

CLINIC_INFO = {
    "name": "Dr. Kevin Smith Harmony Clinic",
    "location": "Harmony Medical Plaza, Suite 203",
    "address": "123 Wellness Drive, Healthville, CA 94123",
    "phone": "(555) 123-4567",
    "hours": {
        "Monday": "8:00 AM - 6:00 PM",
        "Tuesday": "8:00 AM - 6:00 PM",
        "Wednesday": "8:00 AM - 6:00 PM",
        "Thursday": "8:00 AM - 6:00 PM",
        "Friday": "8:00 AM - 6:00 PM",
        "Saturday": "9:00 AM - 2:00 PM",
        "Sunday": "Closed"
    },
    "website": "www.drsmithclinic.example.com",
    "services": ["Primary Care", "Pediatrics", "Vaccinations", "Annual Check-ups", "Lab Tests"]
}

# Available appointment slots
APPOINTMENT_SLOTS = {
    "Monday": ["9:00 AM", "10:30 AM", "1:00 PM", "2:30 PM", "4:00 PM"],
    "Tuesday": ["8:30 AM", "10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM"],
    "Wednesday": ["9:00 AM", "10:30 AM", "1:00 PM", "2:30 PM", "4:00 PM"],
    "Thursday": ["8:30 AM", "10:00 AM", "11:30 AM", "2:00 PM", "3:30 PM"],
    "Friday": ["9:00 AM", "10:30 AM", "1:00 PM", "2:30 PM", "4:00 PM"],
    "Saturday": ["9:30 AM", "11:00 AM", "12:30 PM"]
}

# Accepted insurance providers
INSURANCE_PROVIDERS = {
    "Aetna": {"accepted": True, "coverage_types": ["preventive", "specialist", "emergency"]},
    "Blue Cross Blue Shield": {"accepted": True, "coverage_types": ["preventive", "specialist", "emergency"]},
    "UnitedHealthcare": {"accepted": True, "coverage_types": ["preventive", "specialist", "emergency"]},
    "Medicare": {"accepted": True, "coverage_types": ["preventive", "specialist", "limited emergency"]},
    "Medicaid": {"accepted": True, "coverage_types": ["preventive", "limited specialist"]},
    "Cigna": {"accepted": False, "coverage_types": []}
}

# Clinic doctors
DOCTORS = {
    "Smith": {"specialty": "Family Medicine", "available_days": ["Monday", "Wednesday", "Friday"]},
    "Johnson": {"specialty": "Pediatrics", "available_days": ["Tuesday", "Thursday", "Friday"]},
    "Patel": {"specialty": "Internal Medicine", "available_days": ["Monday", "Tuesday", "Thursday"]}
}