# utils/logging_utils.py

import json
import os
import threading
import time
from datetime import datetime
from utils.colors import Colors

LOGS_FILE = "data/logs.json"

# --- LOGGING UTILITIES ---

def log_feeding_entry(pets: dict, pet_name: str, grams: float, calories: float):
    """Log a feeding entry for a pet."""
    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found." + Colors.RESET)
        return

    today = datetime.today().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    # Initialize logs if missing
    if "feeding_logs" not in pets[pet_name]:
        pets[pet_name]["feeding_logs"] = []

    pets[pet_name]["feeding_logs"].append({
        "date": today,
        "time": time_str,
        "grams": grams,
        "calories": calories
    })

    # Save logs to central file
    _save_log_entry("feeding", pet_name, today, time_str, {"grams": grams, "calories": calories})
    print(f"📝 Logged feeding for {pet_name}: {grams}g ({calories} kcal)")

def log_medication_entry(pets: dict, pet_name: str, dose: str):
    """Log a medication entry for a pet."""
    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found." + Colors.RESET)
        return

    today = datetime.today().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    # Initialize logs if missing
    if "medication_logs" not in pets[pet_name]:
        pets[pet_name]["medication_logs"] = []

    pets[pet_name]["medication_logs"].append({
        "date": today,
        "time": time_str,
        "dose": dose
    })

    _save_log_entry("medication", pet_name, today, time_str, {"dose": dose})
    print(f"📝 Logged medication for {pet_name}: {dose}")

def log_weight_entry(pets: dict, pet_name: str, weight: float):
    """Log a weight entry for a pet."""
    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found." + Colors.RESET)
        return

    today = datetime.today().strftime("%Y-%m-%d")

    # Initialize logs if missing
    if "weight_logs" not in pets[pet_name]:
        pets[pet_name]["weight_logs"] = []

    pets[pet_name]["weight_logs"].append({
        "date": today,
        "weight": weight
    })

    _save_log_entry("weight", pet_name, today, datetime.now().strftime("%H:%M"), {"weight": weight})
    print(f"📝 Logged weight for {pet_name}: {weight}kg")

def _save_log_entry(log_type: str, pet_name: str, date: str, time: str, data: dict):
    """Save a log entry to the central logs.json file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": log_type,
        "pet": pet_name,
        "date": date,
        "time": time,
        "data": data
    }

    # Ensure logs directory exists
    os.makedirs(os.path.dirname(LOGS_FILE), exist_ok=True)

    # Load existing logs
    logs = []
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []
        except Exception:
            logs = []

    # Append new log
    logs.append(log_entry)

    # Save back
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

def toggle_reminder(pets: dict, pet_name: str, reminder_type: str):
    """Toggle feeding or medication reminder for a pet."""
    if pet_name not in pets:
        return

    if reminder_type == "feeding":
        pets[pet_name]["feeding_reminder_enabled"] = not pets[pet_name].get("feeding_reminder_enabled", False)
    elif reminder_type == "medication":
        pets[pet_name]["medication_reminder_enabled"] = not pets[pet_name].get("medication_reminder_enabled", False)

def snooze_reminder(pets: dict, pet_name: str, hours: int):
    """Snooze all reminders for a pet for N hours."""
    if pet_name not in pets:
        return

    snooze_until = (datetime.now().timestamp() + hours * 3600)
    pets[pet_name]["snooze_until"] = snooze_until

def set_quiet_hours(pets: dict, pet_name: str, start: str, end: str):
    """Set quiet hours for a pet."""
    if pet_name not in pets:
        return
    pets[pet_name]["quiet_hours"] = {"start": start, "end": end}

def is_valid_time(time_str: str) -> bool:
    """Validate time format HH:MM."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def print_daily_summary(pets: dict, pet_name=None):
    """
    Print daily summary for a specific pet, or all pets if pet_name is None.
    """
    # If pet_name is provided, show only that pet
    if pet_name:
        if pet_name not in pets:
            print(Colors.RED + "❌ Pet not found." + Colors.RESET)
            return

        pet = pets[pet_name]
        name = pet["name"]
        calories_consumed = sum(log["calories"] for log in pet.get("feeding_logs", []) if log.get("date") == datetime.today().strftime("%Y-%m-%d"))
        calories_target = pet.get("calorie_target", 100.0)
        weight_logs = pet.get("weight_logs", [])
        recent_weight = weight_logs[-1]["weight"] if weight_logs else "N/A"
        recent_weight_date = weight_logs[-1]["date"] if weight_logs else "N/A"

        print(f"🐾 {name}")
        print(f"   🍽️  Calories Consumed: {calories_consumed:.1f} kcal / {calories_target:.1f} kcal target")
        print(f"   ⚖️  Latest Weight: {recent_weight} kg (as of {recent_weight_date})")

        # Show medication logs today
        med_logs = [log for log in pet.get("medication_logs", []) if log.get("date") == datetime.today().strftime("%Y-%m-%d")]
        if med_logs:
            print(f"   💊 Medication: {len(med_logs)} doses today")
            for log in med_logs:
                print(f"      - {log['dose']} at {log['time']}")
        else:
            print(f"   💊 Medication: No doses logged today")

        # Show reminder status
        feed_reminder = "ON" if pet.get("feeding_reminder_enabled", False) else "OFF"
        med_reminder = "ON" if pet.get("medication_reminder_enabled", False) else "OFF"
        print(f"   🔔 Reminders: Feeding: {feed_reminder} | Medication: {med_reminder}")

    else:
        # Legacy: Show for all pets
        print(Colors.CYAN + "📋 DAILY SUMMARY FOR ALL PETS" + Colors.RESET)
        for name, pet in pets.items():
            calories_consumed = sum(log["calories"] for log in pet.get("feeding_logs", []) if log.get("date") == datetime.today().strftime("%Y-%m-%d"))
            calories_target = pet.get("calorie_target", 100.0)
            weight_logs = pet.get("weight_logs", [])
            recent_weight = weight_logs[-1]["weight"] if weight_logs else "N/A"
            recent_weight_date = weight_logs[-1]["date"] if weight_logs else "N/A"

            print(f"\n🐾 {name}")
            print(f"   🍽️  Calories Consumed: {calories_consumed:.1f} kcal / {calories_target:.1f} kcal target")
            print(f"   ⚖️  Latest Weight: {recent_weight} kg (as of {recent_weight_date})")

            # Show medication logs today
            med_logs = [log for log in pet.get("medication_logs", []) if log.get("date") == datetime.today().strftime("%Y-%m-%d")]
            if med_logs:
                print(f"   💊 Medication: {len(med_logs)} doses today")
                for log in med_logs:
                    print(f"      - {log['dose']} at {log['time']}")
            else:
                print(f"   💊 Medication: No doses logged today")

            feed_reminder = "ON" if pet.get("feeding_reminder_enabled", False) else "OFF"
            med_reminder = "ON" if pet.get("medication_reminder_enabled", False) else "OFF"
            print(f"   🔔 Reminders: Feeding: {feed_reminder} | Medication: {med_reminder}")

# --- GRAPHING FUNCTIONS ---
def plot_weight_graph(pets: dict, pet_name: str):
    """Plot today's weight entries for a pet (ASCII bar chart)."""
    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found." + Colors.RESET)
        return

    logs = pets[pet_name].get("weight_logs", [])
    today_logs = [log for log in logs if log["date"] == datetime.today().strftime("%Y-%m-%d")]

    if not today_logs:
        print(Colors.YELLOW + "📭 No weight data logged today." + Colors.RESET)
        return

    print(f"\n{Colors.CYAN}📈 WEIGHT TREND FOR {pet_name.upper()} TODAY{Colors.RESET}")
    print("="*50)
    for log in today_logs:
        weight = log["weight"]
        time_str = log.get("time", "unknown")
        # Scale: 1kg = 5 bars
        bar = "█" * int(weight * 5)
        print(f"   {time_str}: {weight}kg | {bar}")
    print("="*50)

def plot_weekly_weight_trend(pets: dict, pet_name: str):
    """Plot weekly weight trend for a pet (last 7 days)."""
    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found." + Colors.RESET)
        return

    logs = pets[pet_name].get("weight_logs", [])
    if not logs:
        print(Colors.YELLOW + "📭 No weight data logged." + Colors.RESET)
        return

    # Sort logs by date
    logs.sort(key=lambda x: x["date"])
    today = datetime.today()
    week_ago = today.strftime("%Y-%m-%d")
    week_logs = [log for log in logs if log["date"] >= (today - datetime.timedelta(days=6)).strftime("%Y-%m-%d")]

    if not week_logs:
        print(Colors.YELLOW + "📭 Less than a week of weight data." + Colors.RESET)
        return

    print(f"\n{Colors.CYAN}📉 WEEKLY WEIGHT TREND FOR {pet_name.upper()}{Colors.RESET}")
    print("="*60)
    for log in week_logs:
        date_str = log["date"]
        weight = log["weight"]
        # Show as bar: 1kg = 10 chars
        bar = "█" * int(weight * 5)
        print(f"   {date_str}: {weight}kg | {bar}")
    print("="*60)

# --- BACKGROUND REMINDER SCHEDULER ---
def start_feeding_scheduler(pets: dict):
    """
    Start a background thread that checks every minute for feeding reminders.
    Sends notifications if it's time and no snooze/quiet hours are active.
    """
    def check_reminders():
        while True:
            time.sleep(60)  # Check every minute
            now = datetime.now()
            now_time_str = now.strftime("%H:%M")
            now_timestamp = now.timestamp()

            for pet_name, pet in pets.items():
                if not pet.get("feeding_reminder_enabled", False):
                    continue

                # Skip if snoozed
                if pet.get("snooze_until") and now_timestamp < pet["snooze_until"]:
                    continue

                # Skip if in quiet hours
                quiet = pet.get("quiet_hours")
                if quiet:
                    start_time = quiet["start"]
                    end_time = quiet["end"]
                    if is_valid_time(start_time) and is_valid_time(end_time):
                        # Convert to minutes since midnight
                        def time_to_minutes(t):
                            h, m = map(int, t.split(':'))
                            return h * 60 + m

                        now_minutes = now.hour * 60 + now.minute
                        start_minutes = time_to_minutes(start_time)
                        end_minutes = time_to_minutes(end_time)

                        if start_minutes <= end_minutes:
                            # Normal case (e.g., 22:00–06:00)
                            if start_minutes <= now_minutes < end_minutes:
                                continue
                        else:
                            # Overnight (e.g., 22:00–06:00)
                            if now_minutes >= start_minutes or now_minutes < end_minutes:
                                continue

                # Check if it’s time for a scheduled feeding
                schedule = pet.get("feeding_schedule", [])
                for scheduled_time in schedule:
                    if scheduled_time == now_time_str:
                        print(
                            Colors.YELLOW + f"🔔 REMINDER: Time to feed {pet_name} at {now_time_str}!" + Colors.RESET
                        )
                        # Optional: Play sound or send OS notification here
                        # For now, just print
                        break  # Only one reminder per minute

    # Start thread (daemon so it exits when main program exits)
    thread = threading.Thread(target=check_reminders, daemon=True)
    thread.start()
    print(Colors.GREEN + "✅ Background feeding scheduler started." + Colors.RESET)