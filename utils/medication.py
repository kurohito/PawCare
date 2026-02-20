from datetime import datetime

def log_medication(med_name, dose, time=None):
    if not time:
        time = datetime.now().strftime("%H:%M")
    print(f"💊 Logged {med_name} ({dose}) at {time}")