# utils/logging_utils.py
from datetime import datetime, timedelta
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication
import os

LOG_FILE = "logs.txt"

# --- ANSI colors ---
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    END = "\033[0m"

def color_text(text, color):
    return f"{color}{text}{Colors.END}"

# --- General logging ---
def log_action(action: str):
    """Append an action with timestamp to the log file using UTF-8."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}\n")

# --- Feedings ---
def log_feeding_entry(pet, grams):
    calories = calculate_calories(grams, pet.get("calorie_density", 85))
    time = datetime.now().strftime("%H:%M")
    entry = {"grams": grams, "calories": calories, "time": time}
    pet.setdefault("feedings", []).append(entry)
    log_action(f"🐾 Logged feeding for {pet['name']}: {grams}g ({calories} cal)")
    return entry

# --- Medications ---
def log_medication_entry(pet, med_name, dose):
    entry = log_medication(med_name, dose)
    pet.setdefault("medications", []).append(entry)
    log_action(f"💊 Logged medication for {pet['name']}: {med_name} ({dose})")
    return entry

# --- Weight logging ---
def log_weight_entry(pet, weight):
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "weight": weight}
    pet.setdefault("weight_history", []).append(entry)
    pet["weight"] = weight
    log_action(f"⚖️ Updated weight for {pet['name']}: {weight} kg")
    return entry

# --- Weight change calculations ---
def calculate_weight_change(pet):
    history = pet.get("weight_history", [])
    if len(history) < 2:
        return 0.0
    first = history[0]["weight"]
    last = history[-1]["weight"]
    return round(((last - first) / first) * 100, 2)

def calculate_recent_weight_change(pet, days=7):
    history = pet.get("weight_history", [])
    if len(history) < 2:
        return 0.0
    today = datetime.now().date()
    start_date = today - timedelta(days=days-1)
    recent = [entry for entry in history if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= start_date]
    if len(recent) < 2:
        return 0.0
    first = recent[0]["weight"]
    last = recent[-1]["weight"]
    return round(((last - first) / first) * 100, 2)

# --- Daily summary ---
def print_daily_summary(pet):
    print(f"--- {pet['name']} 🌸 ---")
    
    total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
    target = pet.get("calorie_target", 0)
    print(f"Calories today: {total_cal}/{target} cal")
    if total_cal < target:
        print(color_text("⚠️ Below target! Consider giving more food.", Colors.RED))
    
    meds = pet.get("medications", [])
    if meds:
        print("Medications today:")
        for med in meds:
            print(f" - {med['med_name']} ({med['dose']}) at {med['time']}")
    else:
        print(color_text("⚠️ No medications logged today!", Colors.RED))

    weight = pet.get("weight")
    if weight:
        print(f"Weight: ⚖️ {weight} kg")
        total_change = calculate_weight_change(pet)
        weekly_change = calculate_recent_weight_change(pet)
        print(f"Total weight change: {total_change:+.2f}%")
        print(f"Last 7 days change: {weekly_change:+.2f}%")
    else:
        print(color_text("⚠️ No weight logged today!", Colors.RED))
    print()

# --- Full weight graph ---
def plot_weight_graph(pet, width=20):
    history = pet.get("weight_history", [])
    if not history:
        print(color_text("⚠️ No weight history yet!\n", Colors.RED))
        return
    weights = [entry["weight"] for entry in history]
    max_w = max(weights)
    min_w = min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1
    print(f"📊 Weight History for {pet['name']}")
    for entry in history:
        bar_len = max(1, int((entry["weight"] - min_w) / step))
        bar = "▇" * bar_len
        print(f"{entry['date']}: {bar} {entry['weight']} kg")
    print()

# --- Weekly weight trend with colored mini-sparkline ---
def plot_weekly_weight_trend(pet, width=30):
    history = pet.get("weight_history", [])
    if not history:
        print(color_text("⚠️ No weight history yet!\n", Colors.RED))
        return

    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    recent = [entry for entry in history if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= week_ago]
    if not recent:
        print(color_text("⚠️ No weight data for the last 7 days.\n", Colors.RED))
        return

    print(f"📅 Weekly Weight Trend for {pet['name']}")
    print(color_text("Legend: 🟢 Up  ➖ Same  🔻 Down  ▇ Weight bar\n", Colors.CYAN))

    prev_w = None
    weights = [entry["weight"] for entry in recent]
    max_w = max(weights)
    min_w = min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1

    for entry in recent:
        w = entry["weight"]
        if prev_w is None:
            symbol = "➖"
            color = Colors.YELLOW
        elif w > prev_w:
            symbol = "🟢"
            color = Colors.GREEN
        elif w < prev_w:
            symbol = "🔻"
            color = Colors.RED
        else:
            symbol = "➖"
            color = Colors.YELLOW
        prev_w = w

        bar_len = max(1, int((w - min_w) / step))
        bar = color_text("▇" * bar_len, color)
        print(f"{symbol} {entry['date']}: {bar} {w} kg")
    print()