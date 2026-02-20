# utils/logging_utils.py
from datetime import datetime, timedelta
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication

LOG_FILE = "logs.txt"

# --- General logging ---
def log_action(action: str):
    """Append an action with timestamp to the log file (UTF-8 safe)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:  # UTF-8 to handle emojis
        f.write(f"[{timestamp}] {action}\n")

# --- Feedings ---
def log_feeding_entry(pet, grams):
    """Log a feeding entry with calories and time."""
    calories = calculate_calories(grams, pet.get("calorie_density", 85))
    time = datetime.now().strftime("%H:%M")
    entry = {"grams": grams, "calories": calories, "time": time}
    pet.setdefault("feedings", []).append(entry)
    log_action(f"🐾 Logged feeding for {pet['name']}: {grams}g ({calories} cal)")
    return entry

# --- Medications ---
def log_medication_entry(pet, med_name, dose):
    """Log a medication entry with timestamp."""
    entry = log_medication(med_name, dose)
    pet.setdefault("medications", []).append(entry)
    log_action(f"💊 Logged medication for {pet['name']}: {med_name} ({dose})")
    return entry

# --- Daily summary ---
def print_daily_summary(pet):
    """Print a daily summary with calories, medications, and weight."""
    print(f"--- {pet['name']} 🌸 ---")
    
    # Calories
    total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
    target = pet.get("calorie_target", 0)
    print(f"Calories today: {total_cal}/{target} cal")
    if total_cal < target:
        print("⚠️  Below target! Consider giving more food.")
    
    # Medications
    meds = pet.get("medications", [])
    if meds:
        print("Medications today:")
        for med in meds:
            print(f" - {med['med_name']} ({med['dose']}) at {med['time']}")
    else:
        print("⚠️  No medications logged today!")
    
    # Current weight
    weight = pet.get("weight")
    if weight:
        print(f"Weight: ⚖️ {weight} kg")
    else:
        print("⚠️  No weight logged today!")
    print()

# --- Weight logging ---
def log_weight_entry(pet, weight):
    """Log weight with date and timestamp, append to history."""
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "weight": weight}
    pet.setdefault("weight_history", []).append(entry)
    pet["weight"] = weight  # Update current weight
    log_action(f"⚖️ Updated weight for {pet['name']}: {weight} kg")
    return entry

# --- Full weight history ASCII/emoji graph ---
def plot_weight_graph(pet, width=20):
    """Plot full ASCII/emoji graph of weight history."""
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
        bar_len = max(1, int((entry["weight"] - min_w) / step))
        bar = "🌸" * bar_len
        print(f"{entry['date']}: {bar} {entry['weight']} kg")
    print()

# --- Weekly weight trend with emoji indicators ---
def plot_weekly_weight_trend(pet, width=30):
    """Show mini ASCII/emoji graph of weight over the last 7 days with trend symbols."""
    history = pet.get("weight_history", [])
    if not history:
        print("⚠️ No weight history yet!\n")
        return

    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    recent = [entry for entry in history 
              if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= week_ago]

    if not recent:
        print("⚠️ No weight data for the last 7 days.\n")
        return

    weights = [entry["weight"] for entry in recent]
    max_w = max(weights)
    min_w = min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1

    print(f"📅 Weekly Weight Trend for {pet['name']}")
    print("Key: 🟢 Up  ➖ Same  🔻 Down\n")

    prev_weight = None
    for entry in recent:
        w = entry["weight"]
        # Determine trend symbol
        if prev_weight is None:
            symbol = "➖"
        elif w > prev_weight:
            symbol = "🟢"
        elif w < prev_weight:
            symbol = "🔻"
        else:
            symbol = "➖"
        prev_weight = w

        # Calculate bar length
        bar_len = max(1, int((w - min_w) / step))  # at least 1 🌸
        bar = "🌸" * bar_len
        print(f"{symbol} {entry['date']}: {bar} {w} kg")
    print()