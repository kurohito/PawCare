from datetime import datetime

def log_medication(med_name, dose):
    time = datetime.now().strftime("%H:%M")
    return {"med_name": med_name, "dose": dose, "time": time}