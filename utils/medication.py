# utils/medication.py
from datetime import datetime

def log_medication(med_name, dose):
    """
    Create a medication log entry for a pet.
    
    Parameters:
    - med_name (str): Name of the medication.
    - dose (str): Dose given (e.g., '0.5ml').
    
    Returns:
    - dict: A dictionary with medication details and timestamp.
    """
    time = datetime.now().strftime("%H:%M")
    return {
        "med_name": med_name,
        "dose": dose,
        "time": time
    }