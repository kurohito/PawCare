from datetime import datetime, timedelta
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication
import threading
import time
from typing import TypedDict, Dict, List, Union, Optional
# 👇 Define the Pet schema using TypedDict
class Pet(TypedDict):
    name: str
    weight: float
    calorie_target: int
    calorie_density: int
    feedings: List[dict]  # List of feeding entries
    medications: List[dict]  # List of medication entries
    weight_history: List[dict]  # List of weight entries
    feeding_times: List[str]  # e.g., ["09:00", "15:00"]
    reminder_enabled: bool
    snooze_until: Optional[str]  # None or ISO-style string like "2026-02-20 14:30:00"
    quiet_hours: Dict[str, Optional[str]]  # {"start": "21:00", "end": "07:00"}
try:
    from plyer import notification
except ImportError:
    notification = None  # Desktop notifications optional
LOG_FILE = "logs.txt"
# Store running schedulers so we don't duplicate threads
_active_schedulers = {}
# --- ANSI colors ---
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    END = "\033[0m"
def color_text(text, color):
    return f"{color}{text}{Colors.END}"
# =========================================================
# GENERAL LOGGING
# =========================================================
def log_action(action: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}\n")
# =========================================================
# FEEDINGS
# =========================================================
def log_feeding_entry(pet: Pet, grams: float) -> dict:
    calories = calculate_calories(grams, pet.get("calorie_density", 85))
    time_str = datetime.now().strftime("%H:%M")
    entry = {"grams": grams, "calories": calories, "time": time_str}
    pet.setdefault("feedings", []).append(entry)
    log_action(f"🐾 Logged feeding for {pet['name']}: {grams}g ({calories} cal)")
    return entry
# =========================================================
# MEDICATIONS
# =========================================================
def log_medication_entry(pet, med_name, dose):
    entry = log_medication(med_name, dose)
    pet.setdefault("medications", []).append(entry)
    log_action(f"💊 Logged medication for {pet['name']}: {med_name} ({dose})")
    return entry
# =========================================================
# WEIGHT LOGGING
# =========================================================
def log_weight_entry(pet: Pet, weight: float) -> dict:
    entry = {"date": datetime.now().strftime("%Y-%m-%d"), "weight": weight}
    pet.setdefault("weight_history", []).append(entry)
    pet["weight"] = weight
    log_action(f"⚖️ Updated weight for {pet['name']}: {weight} kg")
    return entry
# =========================================================
# WEIGHT CALCULATIONS
# =========================================================
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
# =========================================================
# DAILY SUMMARY
# =========================================================
def print_daily_summary(pet):
    print(f"\n--- {pet['name']} 🌸 ---")
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
        print(f"Total weight change: {calculate_weight_change(pet):+.2f}%")
        print(f"Last 7 days change: {calculate_recent_weight_change(pet):+.2f}%")
    else:
        print(color_text("⚠️ No weight logged yet!", Colors.RED))
    # Reminder status
    reminder_status = "🟢 On" if pet.get("reminder_enabled") else "🔴 Off"
    print(f"Reminder: {reminder_status}\n")
# =========================================================
# WEIGHT GRAPH
# =========================================================
def plot_weight_graph(pet, width=20):
    history = pet.get("weight_history", [])
    if not history:
        print(color_text("⚠️ No weight history yet!\n", Colors.RED))
        return
    weights = [entry["weight"] for entry in history]
    max_w, min_w = max(weights), min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1
    print(f"\n📊 Weight History for {pet['name']}")
    for entry in history:
        bar_len = max(1, int((entry["weight"] - min_w) / step))
        bar = "▇" * bar_len
        print(f"{entry['date']}: {bar} {entry['weight']} kg")
    print()
# =========================================================
# WEEKLY TREND
# =========================================================
def plot_weekly_weight_trend(pet, width=30):
    history = pet.get("weight_history", [])
    if not history:
        print(color_text("⚠️ No weight history yet!\n", Colors.RED))
        return
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)
    recent = [entry for entry in history if datetime.strptime(entry["date"], "%Y-%m-%d").date() >= week_ago]
    if not recent:
        print(color_text("⚠️ No weight data for last 7 days.\n", Colors.RED))
        return
    print(f"📅 Weekly Weight Trend for {pet['name']}")
    prev_w = None
    weights = [entry["weight"] for entry in recent]
    max_w, min_w = max(weights), min(weights)
    step = (max_w - min_w) / width if max_w != min_w else 1
    for entry in recent:
        w = entry["weight"]
        symbol = "➖"
        color = Colors.YELLOW
        if prev_w is not None:
            if w > prev_w:
                symbol = "🟢"
                color = Colors.GREEN
            elif w < prev_w:
                symbol = "🔻"
                color = Colors.RED
        bar_len = max(1, int((w - min_w) / step))
        bar = color_text("▇" * bar_len, color)
        print(f"{symbol} {entry['date']}: {bar} {w} kg")
        prev_w = w
    print()
# =========================================================
# REMINDER HELPERS
# =========================================================
def toggle_reminder(pet):
    pet["reminder_enabled"] = not pet.get("reminder_enabled", True)
    status = "enabled" if pet["reminder_enabled"] else "disabled"
    log_action(f"🔔 Reminder {status} for {pet['name']}")
    if pet["reminder_enabled"]:
        start_feeding_scheduler(pet)
    print(f"✅ Reminder {status} for {pet['name']}.")
def snooze_reminder(pet, minutes):
    pet["snooze_until"] = (datetime.now() + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    log_action(f"😴 Reminder snoozed for {minutes} minutes for {pet['name']}")
    print(f"✅ Reminder snoozed for {minutes} minutes.")
def set_quiet_hours(pet, start_time, end_time):
    pet["quiet_hours"] = {"start": start_time, "end": end_time}
    log_action(f"🛏️ Quiet hours set for {pet['name']}: {start_time} - {end_time}")
    print(f"✅ Quiet hours set: {start_time} - {end_time}")
# =========================================================
# FEEDING SCHEDULER
# =========================================================
def start_feeding_scheduler(pet: Pet, pets_dict: Dict[str, Pet]):
    """
    Start a background feeding scheduler thread for a pet.
    
    Args:
        pet (Pet): The pet dictionary to schedule for.
        pets_dict (Dict[str, Pet]): The global pets dictionary {id: pet} to find pet's key.
    """
    pet_name = pet["name"]
    pet_id = None
    for key, p in pets_dict.items():
        if p == pet:
            pet_id = key
            break
    if not pet_id:
        print(f"⚠️ Could not find pet ID for {pet_name} in pets dict. Reminders not started.")
        return
    pet_key = f"{pet_name}_{pet_id}"
    if pet_key in _active_schedulers:
        return
    feeding_times = pet.get("feeding_times", [])
    if not feeding_times or not pet.get("reminder_enabled", False):
        return
    def scheduler_loop():
        notified_today = set()
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            today_date = now.strftime("%Y-%m-%d")
            # Check quiet hours
            q_start = pet.get("quiet_hours", {}).get("start")
            q_end = pet.get("quiet_hours", {}).get("end")
            in_quiet = False
            if q_start and q_end:
                if q_start <= current_time <= q_end:
                    in_quiet = True
            # Check snooze
            snooze_until = pet.get("snooze_until")
            if snooze_until:
                try:
                    snooze_dt = datetime.strptime(snooze_until, "%Y-%m-%d %H:%M:%S")
                    if now < snooze_dt:
                        in_quiet = True
                except ValueError:
                    pass  # Invalid snooze time, ignore
            for ft in feeding_times:
                key = f"{today_date}_{ft}"
                if current_time == ft and key not in notified_today and not in_quiet:
                    msg = f"Time to feed {pet_name} ({ft})!"
                    print(f"\n🔔 {msg}\n")
                    log_action(f"🔔 Feeding reminder triggered for {pet_name} ({ft})")
                    if notification:
                        try:
                            notification.notify(title="🐾 Feeding Reminder", message=msg, timeout=10)
                        except Exception as e:
                            print(f"⚠️ Notification error: {e}")
                    notified_today.add(key)
            time.sleep(30)
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    _active_schedulers[pet_key] = thread