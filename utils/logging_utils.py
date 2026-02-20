# utils/logging_utils.py

import json
import os
import datetime
from utils.colors import Colors

# --- FILE PATHS ---
PET_DATA_FILE = "data/pets.json"
LOGS_FILE = "data/logs.json"
USER_PREFS_FILE = "data/user_prefs.json"

# --- HELPER: Load Pet Data ---
def load_pets():
    if not os.path.exists(PET_DATA_FILE):
        return {}
    try:
        with open(PET_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(Colors.RED + "❌ Corrupted pets.json. Starting fresh." + Colors.RESET)
        return {}

# --- HELPER: Save Pet Data ---
def save_pets(pets):
    os.makedirs("data", exist_ok=True)
    with open(PET_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(pets, f, indent=2, ensure_ascii=False)

# --- HELPER: Load User Preferences ---
def load_user_prefs():
    if not os.path.exists(USER_PREFS_FILE):
        # File doesn't exist → create it
        save_user_prefs({"unit": "kg"})
        return {"unit": "kg"}
    try:
        with open(USER_PREFS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and "unit" in data and data["unit"] in ["kg", "lb"]:
                return data
            else:
                # Invalid structure → reset
                print(Colors.YELLOW + "⚠️  Invalid user_prefs.json structure. Resetting to default." + Colors.RESET)
                save_user_prefs({"unit": "kg"})
                return {"unit": "kg"}
    except (json.JSONDecodeError, UnicodeDecodeError, PermissionError):
        print(Colors.YELLOW + "⚠️  Corrupted or unreadable user_prefs.json. Resetting to default." + Colors.RESET)
        save_user_prefs({"unit": "kg"})
        return {"unit": "kg"}

# --- HELPER: Save User Preferences ---
def save_user_prefs(prefs):
    os.makedirs("data", exist_ok=True)
    with open(USER_PREFS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)

# --- LOGGING FUNCTIONS ---
def log_feeding_entry(pets, pet_name, grams, calories):
    if pet_name not in pets:
        return
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "grams": grams,
        "calories": calories
    }
    pets[pet_name].setdefault("feedings", []).append(entry)
    save_pets(pets)

def log_medication_entry(pets, pet_name, dose):
    if pet_name not in pets:
        return
    # Find the medication being logged (by dose) — assumes exactly one match
    meds = pets[pet_name].get("medications", [])
    for med in meds:
        if med["dose"] == dose:
            # Update next_due based on interval
            now = datetime.datetime.now()
            if med.get("interval_hours"):
                next_due = now + datetime.timedelta(hours=med["interval_hours"])
                med["next_due"] = next_due.strftime("%Y-%m-%d %H:%M")
            else:
                # One-time med: mark as "used" — no next_due
                med["next_due"] = "used"
            break
    # Log in external logs file
    log_entry = {
        "type": "medication",
        "pet": pet_name,
        "medication": dose,
        "timestamp": datetime.datetime.now().isoformat()
    }
    log_to_file(log_entry)
    save_pets(pets)

def log_weight_entry(pets, pet_name, weight):
    if pet_name not in pets:
        return
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "weight": weight,
        "unit": load_user_prefs().get("unit", "kg")
    }
    pets[pet_name].setdefault("weights", []).append(entry)
    save_pets(pets)

# --- LOG FILE (separate from pet data) ---
def log_to_file(entry):
    os.makedirs("data", exist_ok=True)
    logs = []
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass
    logs.append(entry)
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# --- VIEW UPCOMING MEDICATIONS ---
def view_upcoming_medications(pets: dict):
    """
    Displays ALL upcoming medication doses within the next 3 days (72 hours).
    Shows every single dose for repeating medications — even if originally set to 2026.
    """
    if not pets:
        print("\n" + "="*70)
        print(Colors.YELLOW + "⚠️  No pets found. Add a pet first!" + Colors.RESET)
        print("="*70)
        input("\nPress Enter to return to main menu...")
        return

    upcoming = get_upcoming_medications(pets)

    print("\n" + "="*70)
    print(Colors.BOLD + "⏰ UPCOMING MEDICATIONS (Next 3 Days)" + Colors.RESET)
    print("="*70)

    if not upcoming:
        print(Colors.YELLOW + "✅ No medications due in the next 3 days." + Colors.RESET)
    else:
        for pet, name, dose, due_dt, interval in upcoming:
            due_str = due_dt.strftime("%Y-%m-%d at %H:%M")
            if interval:
                status = f"🔁 Every {interval}h"
                due_str += f" ({status})"
            print(f"{Colors.GREEN}{pet}{Colors.RESET} — {name} — {dose} — Due: {due_str}")

    print("="*70)
    input("\nPress Enter to return to main menu...")


def get_upcoming_medications(pets: dict) -> list:
    """
    Returns list of tuples: (pet_name, med_name, dose, due_datetime, interval_hours)
    Calculates next 72 hours of doses from current time.
    Ignores year/month/day — only uses time-of-day (HH:MM) and interval.
    """
    now = datetime.datetime.now()
    end_time = now + datetime.timedelta(hours=72)  # 3 days
    upcoming = []

    for pet_name, pet_data in pets.items():
        meds = pet_data.get("medications", [])
        for med in meds:
            name = med["name"]
            dose = med["dose"]
            interval_hours = med.get("interval_hours")
            next_due_str = med.get("next_due", "2026-01-01 00:00")

            # Extract HH:MM from next_due (ignore date)
            try:
                next_due_dt = datetime.datetime.strptime(next_due_str, "%Y-%m-%d %H:%M")
                base_time = next_due_dt.time()
            except ValueError:
                # If invalid, assume 00:00
                base_time = datetime.time(0, 0)

            if interval_hours is None:
                # One-time medication
                if next_due_str != "used":
                    due_dt = datetime.datetime.combine(now.date(), base_time)
                    if now <= due_dt <= end_time:
                        upcoming.append((pet_name, name, dose, due_dt, None))
            else:
                # Repeating medication
                # Start from today at base_time
                current_date = now.date()
                # First candidate: today at base_time
                due_dt = datetime.datetime.combine(current_date, base_time)
                # If due_dt is in past, find next occurrence
                if due_dt < now:
                    due_dt += datetime.timedelta(hours=interval_hours)
                # Generate all due times until end_time
                while due_dt <= end_time:
                    upcoming.append((pet_name, name, dose, due_dt, interval_hours))
                    due_dt += datetime.timedelta(hours=interval_hours)

    # Sort by due date
    upcoming.sort(key=lambda x: x[3])
    return upcoming

# --- MANAGE MEDICATIONS (NEW FUNCTION) ---
def manage_medications(pets: dict):
    """
    Interactive menu to add, edit, or remove medications for a pet.
    Updates pet data and saves to file.
    """
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets found. Add a pet first!" + Colors.RESET)
        input("Press Enter to return...")
        return

    print("\nAvailable pets:")
    for name in pets.keys():
        print(f"  - {name}")
    pet_name = input("\nEnter pet name to manage medications: ").strip()

    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        input("Press Enter to return...")
        return

    pet = pets[pet_name]
    meds = pet.get("medications", [])

    while True:
        print(f"\n🩺 Managing medications for {pet_name}")
        if not meds:
            print("  No medications set.")
        else:
            for i, med in enumerate(meds, 1):
                interval = f" (Every {med['interval_hours']}h)" if med.get("interval_hours") else " (One-time)"
                next_due = med.get("next_due", "N/A")
                print(f"  {i}. {med['name']} — {med['dose']}{interval} — Next: {next_due}")

        print("\nOptions:")
        print("  1. Add Medication")
        print("  2. Edit Medication")
        print("  3. Remove Medication")
        print("  4. Back to Settings")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            med_name = input("Medication name: ").strip()
            if not med_name:
                print(Colors.RED + "❌ Medication name cannot be empty!" + Colors.RESET)
                continue
            dose = input("Dose (e.g., 0.5ml per ear): ").strip()
            if not dose:
                print(Colors.RED + "❌ Dose cannot be empty!" + Colors.RESET)
                continue
            interval_input = input("Repeat every ? hours (leave blank for one-time): ").strip()
            interval_hours = int(interval_input) if interval_input.isdigit() else None
            # Use a placeholder next_due — it will be recalculated on first log or view
            med = {
                "name": med_name,
                "dose": dose,
                "interval_hours": interval_hours,
                "next_due": "2026-01-01 00:00"  # placeholder — will be auto-calculated
            }
            meds.append(med)
            print(Colors.GREEN + f"✅ Added: {med_name}" + Colors.RESET)

        elif choice == "2":
            if not meds:
                print(Colors.YELLOW + "⚠️  No medications to edit." + Colors.RESET)
                continue
            try:
                idx = int(input("Enter number to edit: ")) - 1
                if 0 <= idx < len(meds):
                    med = meds[idx]
                    print(f"Editing: {med['name']} — {med['dose']}")
                    new_name = input(f"New name (current: {med['name']}): ").strip()
                    if new_name:
                        med["name"] = new_name
                    new_dose = input(f"New dose (current: {med['dose']}): ").strip()
                    if new_dose:
                        med["dose"] = new_dose
                    interval_input = input(f"New interval (current: {med.get('interval_hours', 'one-time')}h, leave blank to disable): ").strip()
                    if interval_input == "":
                        med["interval_hours"] = None
                    elif interval_input.isdigit():
                        med["interval_hours"] = int(interval_input)
                    else:
                        print(Colors.RED + "❌ Invalid interval. Keeping current." + Colors.RESET)
                    # Reset next_due to force recalculation
                    med["next_due"] = "2026-01-01 00:00"
                    print(Colors.GREEN + "✅ Medication updated!" + Colors.RESET)
                else:
                    print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
            except ValueError:
                print(Colors.RED + "❌ Invalid input." + Colors.RESET)

        elif choice == "3":
            if not meds:
                print(Colors.YELLOW + "⚠️  No medications to remove." + Colors.RESET)
                continue
            try:
                idx = int(input("Enter number to remove: ")) - 1
                if 0 <= idx < len(meds):
                    removed = meds.pop(idx)
                    print(Colors.GREEN + f"✅ Removed: {removed['name']}" + Colors.RESET)
                else:
                    print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
            except ValueError:
                print(Colors.RED + "❌ Invalid input." + Colors.RESET)

        elif choice == "4":
            save_pets(pets)
            print(Colors.GREEN + "✅ Changes saved. Returning to Settings..." + Colors.RESET)
            break
        else:
            print(Colors.RED + "❌ Invalid option." + Colors.RESET)

# --- CHANGE WEIGHT UNIT ---
def change_weight_unit():
    prefs = load_user_prefs()
    current = prefs.get("unit", "kg").upper()
    print(f"Current unit: {current}")
    new_unit = input("Enter new unit (kg or lb): ").strip().lower()
    if new_unit in ["kg", "lb"]:
        prefs["unit"] = new_unit
        save_user_prefs(prefs)
        print(Colors.GREEN + f"✅ Weight unit changed to {new_unit.upper()}!" + Colors.RESET)
    else:
        print(Colors.RED + "❌ Invalid unit. Use 'kg' or 'lb'." + Colors.RESET)

# --- DELETE ALL DATA ---
def delete_all_data():
    confirm = input("⚠️  Are you sure you want to delete ALL pet data and logs? (y/N): ").strip().lower()
    if confirm == "y":
        files = [PET_DATA_FILE, LOGS_FILE, USER_PREFS_FILE]
        for f in files:
            if os.path.exists(f):
                os.remove(f)
        print(Colors.GREEN + "✅ All data deleted!" + Colors.RESET)
    else:
        print(Colors.YELLOW + "❌ Deletion cancelled." + Colors.RESET)

# --- RESET USER PREFERENCES ---
def reset_user_prefs():
    confirm = input("⚠️  Reset all user preferences to default? (y/N): ").strip().lower()
    if confirm == "y":
        save_user_prefs({"unit": "kg"})
        print(Colors.GREEN + "✅ Preferences reset to default." + Colors.RESET)
    else:
        print(Colors.YELLOW + "❌ Reset cancelled." + Colors.RESET)

# --- DAILY SUMMARY ---
def print_daily_summary(pets: dict):
    print("\n" + "="*60)
    print(Colors.BOLD + "📅 DAILY SUMMARY" + Colors.RESET)
    print("="*60)

    if not pets:
        print(Colors.YELLOW + "No pets registered." + Colors.RESET)
        return

    today = datetime.date.today()
    today_str = today.isoformat()

    for pet_name, data in pets.items():
        print(f"\n🐾 {pet_name}")

        # Feedings today
        feedings = data.get("feedings", [])
        today_feedings = [f for f in feedings if f["timestamp"].startswith(today_str)]
        total_grams = sum(f["grams"] for f in today_feedings)
        total_calories = sum(f["calories"] for f in today_feedings)
        print(f"  🍽️  Feedings: {len(today_feedings)} meals — {total_grams}g — {total_calories} kcal")

        # Weights today
        weights = data.get("weights", [])
        today_weights = [w for w in weights if w["timestamp"].startswith(today_str)]
        if today_weights:
            latest_weight = today_weights[-1]["weight"]
            unit = today_weights[-1].get("unit", "kg")
            print(f"  ⚖️   Weight: {latest_weight} {unit.upper()}")

        # Medications due today
        upcoming = get_upcoming_medications({pet_name: data})
        due_today = [m for m in upcoming if m[3].date() == today]
        if due_today:
            print(f"  💊 Medications due today: {len(due_today)}")
            for _, name, dose, due_dt, _ in due_today:
                print(f"    - {name}: {dose} at {due_dt.strftime('%H:%M')}")

    print("="*60)
    input("Press Enter to return...")

# --- WEEKLY WEIGHT TREND ---
def plot_weekly_weight_trend(pets: dict):
    import matplotlib.pyplot as plt

    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to plot." + Colors.RESET)
        input("Press Enter to return...")
        return

    plt.figure(figsize=(10, 5))
    for pet_name, data in pets.items():
        weights = data.get("weights", [])
        if not weights:
            continue
        # Sort by date
        weights.sort(key=lambda x: x["timestamp"])
        dates = [datetime.datetime.fromisoformat(w["timestamp"]) for w in weights]
        values = [w["weight"] for w in weights]
        plt.plot(dates, values, marker='o', label=pet_name)

    if len(plt.gca().lines) == 0:
        print(Colors.YELLOW + "⚠️  No weight data to plot." + Colors.RESET)
        input("Press Enter to return...")
        return

    plt.title("🐾 Weekly Weight Trend")
    plt.xlabel("Date")
    plt.ylabel(f"Weight ({load_user_prefs().get('unit', 'kg').upper()})")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()