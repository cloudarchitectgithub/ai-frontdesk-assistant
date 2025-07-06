class InsuranceVerifier:
    def __init__(self):
        self.accepted_providers = {
            "XYZ Health": {"coverage": ["general checkup", "vaccinations"]},
            "ABC Insurance": {"coverage": ["general checkup", "specialist visits"]},
            # Add more providers...
        }
        
    def verify_insurance(self, provider, policy_number):
        if provider in self.accepted_providers:
            return f"Verified - {provider} policy {policy_number} is accepted"
        return f"Sorry, we don't accept {provider}"