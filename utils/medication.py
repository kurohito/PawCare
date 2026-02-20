# utils/medication.py
from datetime import datetime

def log_medication(med_name, dose):
    """
    Create a medication log entry for a pet.
    
    Returns:
    - dict with name, dose, and timestamp
    """
    time = datetime.now().strftime("%H:%M")
    return {"med_name": med_name, "dose": dose, "time": time}