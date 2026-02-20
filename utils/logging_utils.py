# utils/logging_utils.py
from datetime import datetime
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication

# Feedings
def log_feeding_entry(pet, grams):
    calories = calculate_calories(grams, pet["cal_per_100g"])
    time = datetime.now().strftime("%H:%M")
    entry = {"grams": grams, "calories": calories, "time": time}
    pet.setdefault("feedings", []).append(entry)
    return entry

# Medications
def log_medication_entry(pet, med_name, dose):
    entry = log_medication(med_name, dose)
    pet.setdefault("medications", []).append(entry)
    return entry

# Daily summary
def print_daily_summary(pet):
    print(f"--- {pet['name']} ---")
    total_cal = sum(f["calories"] for f in pet.get("feedings", []))
    target = pet.get("cal_target", 0)
    print(f"Calories today: {total_cal}/{target} cal")
    if total_cal < target:
        print("⚠️  Below target! Consider giving more food.")
    meds = pet.get("medications", [])
    if meds:
        print("Medications today:")
        for med in meds:
            print(f" - {med['med_name']} ({med['dose']}) at {med['time']}")
    else:
        print("⚠️  No medications logged today!")
    print()

# Weight
def log_weight_entry(pet, weight):
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "weight": weight}
    pet.setdefault("weight_history", []).append(entry)
    return entry

def plot_weight_graph(pet, width=20):
    history = pet.get("weight_history", [])
    if not history:
        print("⚠️ No weight history yet!\n")
        return
    weights = [entry["weight"] for entry in history]
    max_w = max(weights)
    min_w = min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1
    print(f"📊 Weight History for {pet['name']}")
    for entry in history:
        bar_len = int((entry["weight"] - min_w) / step)
        bar = "🌸" * bar_len
        print(f"{entry['date']}: {bar} {entry['weight']} kg")
    print()