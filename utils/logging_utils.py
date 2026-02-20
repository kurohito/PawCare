# utils/logging_utils.py
from datetime import datetime
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication

def log_feeding_entry(pet, grams):
    """
    Logs a feeding for a given pet.
    
    Parameters:
    - pet (dict): Pet dictionary from pets.json
    - grams (float): Amount of food fed in grams
    
    Returns:
    - dict: Feeding entry with grams, calories, and timestamp
    """
    calories = calculate_calories(grams, pet["cal_per_100g"])
    time = datetime.now().strftime("%H:%M")
    entry = {"grams": grams, "calories": calories, "time": time}
    pet["feedings"].append(entry)
    return entry

def log_medication_entry(pet, med_name, dose):
    """
    Logs a medication for a given pet.
    
    Parameters:
    - pet (dict): Pet dictionary from pets.json
    - med_name (str): Name of medication
    - dose (str): Dose given (e.g., "0.5ml")
    
    Returns:
    - dict: Medication entry with name, dose, and timestamp
    """
    entry = log_medication(med_name, dose)
    pet["medications"].append(entry)
    return entry

def print_daily_summary(pet):
    """
    Prints a daily summary for a single pet.
    """
    print(f"--- {pet['name']} ---")
    # Calories summary
    total_cal = sum(f["calories"] for f in pet.get("feedings", []))
    target = pet.get("cal_target", 0)
    print(f"Calories today: {total_cal}/{target} cal")
    if total_cal < target:
        print("⚠️  Below target! Consider giving more food.")
    
    # Medications summary
    meds = pet.get("medications", [])
    if meds:
        print("Medications given today:")
        for med in meds:
            print(f" - {med['med_name']} ({med['dose']}) at {med['time']}")
    else:
        print("⚠️  No medications logged today!")
    print()  # spacing