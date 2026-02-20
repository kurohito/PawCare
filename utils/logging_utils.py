# utils/logging_utils.py
from datetime import datetime, timedelta
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication
from utils.colors import color_text, Colors
import os

LOG_FILE = "logs.txt"

# --- General logging ---
def log_action(action: str):
    """Append an action with timestamp to the log file using UTF-8."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
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

# --- Weight logging ---
def log_weight_entry(pet, weight):
    """Log weight with date and timestamp, append to history."""
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "weight": weight}
    pet.setdefault("weight_history", []).append(entry)
    pet["weight"] = weight  # Update current weight
    log_action(f"⚖️ Updated weight for {pet['name']}: {weight} kg")
    return entry

# --- Weight change calculations ---
def calculate_weight_change(pet):
    """Return percentage change from first to last weight entry."""
    history = pet.get("weight_history", [])
    if len(history) < 2:
        return 0.0
    first = history[0]["weight"]
    last = history[-1]["weight"]
    return round(((last - first) / first) * 100, 2)

def calculate_recent_weight_change(pet, days=7):
    """Return percentage change over last N days."""
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
    """Print a daily summary with calories, medications, weight, and % change."""
    print(f"--- {pet['name']} 🌸 ---")
    
    # Calories
    total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
    target = pet.get("calorie_target", 0)
    cal_msg = f"Calories today: {total_cal}/{target} cal"
    if total_cal < target:
        cal_msg = color_text(cal_msg + " ⚠️ Below target!", Colors.RED)
    print(cal_msg)
    
    # Medications
    meds = pet.get("medications", [])
    if meds:
        print("Medications today:")
        for med in meds:
            print(f" - {med['med_name']} ({med['dose']}) at {med['time']}")
    else:
        print(color_text("⚠️ No medications logged today!", Colors.RED))

    # Current weight
    weight = pet.get("weight")
    if weight:
        print(f"Weight: ⚖️ {weight} kg")
        total_change = calculate_weight_change(pet)
        weekly_change = calculate_recent_weight_change(pet)

        # Total change
        if total_change <= -5:
            print(color_text(f"⚠️ Total weight change: {total_change:+.2f}%", Colors.RED))
        elif total_change >= 5:
            print(color_text(f"🟢 Total weight change: {total_change:+.2f}%", Colors.GREEN))
        else:
            print(color_text(f"➖ Total weight change: {total_change:+.2f}%", Colors.YELLOW))

        # Weekly change
        if weekly_change <= -5:
            print(color_text(f"⚠️ Last 7 days change: {weekly_change:+.2f}%", Colors.RED))
        elif weekly_change >= 5:
            print(color_text(f"🟢 Last 7 days change: {weekly_change:+.2f}%", Colors.GREEN))
        else:
            print(color_text(f"➖ Last 7 days change: {weekly_change:+.2f}%", Colors.YELLOW))
    else:
        print(color_text("⚠️ No weight logged today!", Colors.RED))
    print()

# --- Full weight graph ---
def plot_weight_graph(pet, width=20):
    """Plot full ASCII/emoji graph of weight history."""
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
        bar = "🌸" * bar_len
        print(f"{entry['date']}: {bar} {entry['weight']} kg")
    print()

# --- Weekly weight trend ---
def plot_weekly_weight_trend(pet, width=30):
    """Show mini ASCII/emoji graph of weight over last 7 days with trend symbols."""
    history = pet.get("weight_history", [])
    if not history:
        print(color_text("⚠️ No weight history yet!\n", Colors.RED))
        return

    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    recent = [entry for entry in history 
              if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= week_ago]

    if not recent:
        print(color_text("⚠️ No weight data for the last 7 days.\n", Colors.RED))
        return

    weights = [entry["weight"] for entry in recent]
    max_w = max(weights)
    min_w = min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1

    print(f"📅 Weekly Weight Trend for {pet['name']}")
    print("Key: 🟢 Up  ➖ Same  🔻 Down  🌸 Weight bar\n")

    prev_weight = None
    for entry in recent:
        w = entry["weight"]
        # Trend symbol
        if prev_weight is None:
            symbol = color_text("➖", Colors.YELLOW)
        elif w > prev_weight:
            symbol = color_text("🟢", Colors.GREEN)
        elif w < prev_weight:
            symbol = color_text("🔻", Colors.RED)
        else:
            symbol = color_text("➖", Colors.YELLOW)
        prev_weight = w

        # Bar length
        bar_len = max(1, int((w - min_w) / step))  # at least 1 🌸
        bar = "🌸" * bar_len
        print(f"{symbol} {entry['date']}: {bar} {w} kg")
    print()