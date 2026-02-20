import os
import json
import datetime
from datetime import datetime, timedelta
from utils.colors import Colors

# --- DATA FILE PATHS ---
PETS_FILE = "data/pets.json"
LOGS_FILE = "data/logs.json"
USER_PREFS_FILE = "data/user_prefs.json"

# --- HELPER FUNCTIONS ---
def load_pets():
    if not os.path.exists(PETS_FILE):
        return {}
    try:
        with open(PETS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_pets(pets):
    os.makedirs("data", exist_ok=True)
    with open(PETS_FILE, 'w') as f:
        json.dump(pets, f, indent=2)

def load_user_prefs():
    if not os.path.exists(USER_PREFS_FILE):
        return {"unit": "kg"}
    try:
        with open(USER_PREFS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"unit": "kg"}

def save_user_prefs(prefs):
    os.makedirs("data", exist_ok=True)
    with open(USER_PREFS_FILE, 'w') as f:
        json.dump(prefs, f, indent=2)

def color_text(text, color):
    return f"{color}{text}{Colors.RESET}"

# --- NEW HELPER: Select Pet by Number ---
def select_pet(pets):
    """
    Displays numbered list of pets and returns the chosen pet name.
    Returns None if no pets or invalid selection.
    """
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets available. Add a pet first." + Colors.RESET)
        return None

    print("\n" + "="*40)
    print(color_text("🐾 SELECT A PET", Colors.BLUE))
    print("="*40)

    pet_list = list(pets.keys())
    for i, name in enumerate(pet_list, 1):
        print(f"{i}. {name}")

    print("0. Cancel")
    print("-" * 40)

    try:
        choice = int(input("Choose pet by number: ").strip())
        if choice == 0:
            return None
        if 1 <= choice <= len(pet_list):
            return pet_list[choice - 1]
        else:
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
            return None
    except ValueError:
        print(Colors.RED + "❌ Please enter a number." + Colors.RESET)
        return None

# --- NEW HELPER: Normalize feeding_schedule to floats ---
def normalize_feeding_schedule(pets):
    """
    Ensures feeding_schedule is a list of floats, not strings.
    Fixes legacy data corruption (e.g., ["250", "300"] → [250.0, 300.0]).
    """
    for pet_name, pet in pets.items():
        schedule = pet.get("feeding_schedule")
        if isinstance(schedule, list):
            cleaned = []
            for item in schedule:
                try:
                    cleaned.append(float(item))
                except (ValueError, TypeError):
                    continue  # Skip invalid entries
            pet["feeding_schedule"] = cleaned

# --- LOGGING FUNCTIONS ---
def log_feeding_entry(pets):
    """
    Log a feeding entry for a selected pet (by number), with option to use
    current time or enter a custom date/time.
    """
    pet_name = select_pet(pets)
    if not pet_name:
        return

    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        return

    food_name = input("Enter food name: ").strip()
    if not food_name:
        print(Colors.RED + "❌ Food name cannot be empty." + Colors.RESET)
        return

    # Get amount in grams
    try:
        grams = float(input("Enter food amount in grams: ").strip())
        if grams <= 0:
            print(Colors.RED + "❌ Grams must be positive." + Colors.RESET)
            return
    except ValueError:
        print(Colors.RED + "❌ Invalid number." + Colors.RESET)
        return

    # Calculate calories if possible
    calories_per_100g = pets[pet_name].get("calories_per_100g")
    total_calories = None
    if calories_per_100g:
        total_calories = (grams / 100) * calories_per_100g
        print(f"💡 Auto-calculated: {total_calories:.1f} kcal")

    # Ask user: current time or custom?
    print("\nWhen was this meal fed?")
    print("1. Use current date/time")
    print("2. Enter custom date/time (YYYY-MM-DD HH:MM)")
    time_choice = input("Choose (1 or 2): ").strip()

    if time_choice == "1":
        meal_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif time_choice == "2":
        while True:
            custom_time = input("Enter date/time (e.g., 2025-04-05 08:30): ").strip()
            try:
                # Parse and validate
                dt = datetime.strptime(custom_time, "%Y-%m-%d %H:%M")
                meal_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                break
            except ValueError:
                print(Colors.RED + "❌ Invalid format. Use YYYY-MM-DD HH:MM (e.g., 2025-04-05 08:30)" + Colors.RESET)
    else:
        print(Colors.RED + "❌ Invalid choice. Using current time." + Colors.RESET)
        meal_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Optional notes
    notes = input("Add notes (optional): ").strip() or ""

    # Create log entry
    log_entry = {
        "food_name": food_name,
        "grams": grams,
        "calories": round(total_calories, 2) if total_calories is not None else None,
        "time": meal_time,
        "notes": notes
    }

    # Add to pet's feedings list
    pets[pet_name].setdefault("feedings", []).append(log_entry)
    save_pets(pets)

    # Confirm
    cal_str = f" ({total_calories:.1f} kcal)" if total_calories is not None else " (calories unknown)"
    print(Colors.GREEN + f"✅ Logged: {grams}g of {food_name}{cal_str} at {meal_time}" + Colors.RESET)

def log_medication_entry(pets):
    """
    Log a medication entry for a selected pet (by number).
    """
    pet_name = select_pet(pets)
    if not pet_name:
        return

    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        return

    medication = input("Medication name: ").strip()
    if not medication:
        print(Colors.RED + "❌ Medication name cannot be empty!" + Colors.RESET)
        return

    dose = input("Dose (e.g., 0.5ml): ").strip()
    if not dose:
        print(Colors.RED + "❌ Dose cannot be empty!" + Colors.RESET)
        return

    notes = input("📝 Optional notes: ").strip() or ""

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "medication": medication,
        "dose": dose,
        "notes": notes,
        "taken": True
    }

    pets[pet_name].setdefault("medications", []).append(entry)
    save_pets(pets)
    print(Colors.GREEN + "✅ Medication logged as taken!" + Colors.RESET)

def log_weight_entry(pets):
    """
    Log a weight entry for a selected pet (by number).
    """
    pet_name = select_pet(pets)
    if not pet_name:
        return

    if pet_name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        return

    try:
        weight = float(input("Enter weight in kg: ").strip())
        if weight <= 0:
            print(Colors.RED + "❌ Weight must be positive." + Colors.RESET)
            return
    except ValueError:
        print(Colors.RED + "❌ Invalid number." + Colors.RESET)
        return

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "weight": weight
    }

    pets[pet_name].setdefault("weights", []).append(entry)
    save_pets(pets)
    print(Colors.GREEN + "✅ Weight logged!" + Colors.RESET)

# --- VIEWING & ANALYTICS ---
def print_daily_summary(pets):
    today_str = datetime.now().strftime("%Y-%m-%d")
    print("\n" + "="*50)
    print(color_text("📊 DAILY SUMMARY", Colors.CYAN + Colors.BOLD))
    print("="*50)

    for pet_name, pet in pets.items():
        print(f"\n{Colors.BOLD}{pet_name}{Colors.RESET}")

        # Feedings
        feedings = pet.get("feedings", [])
        total_calories = sum(f.get("calories", 0) for f in feedings)
        target = pet.get("target_daily_calories", 0)
        if target:
            percent = (total_calories / target) * 100 if target > 0 else 0
            print(f"   🍽️  Feedings: {len(feedings)} meals | {total_calories:.1f} kcal / {target} kcal ({percent:.0f}%)")
            if feedings:
                print("      Last meal: " + format_time_for_display(feedings[-1]["time"]))

        # Medications (today or overdue)
        meds_today = []
        if "medications" in pet:
            for med in pet["medications"]:
                next_due = med.get("next_due")
                if not next_due:
                    continue
                try:
                    if " " in next_due:
                        due_dt = datetime.strptime(next_due, "%Y-%m-%d %H:%M")
                    else:
                        due_dt = datetime.strptime(next_due, "%Y-%m-%d")
                except ValueError:
                    continue
                if due_dt.date() <= datetime.now().date() and not med.get("taken", False):
                    meds_today.append(med)

        if meds_today:
            print(color_text(f"   💊 Medications due TODAY ({len(meds_today)} total):", Colors.RED))
            for med in meds_today:
                due_time = med.get("dosing_time", "")
                status = format_medication_status(med)
                color = Colors.RED if status == "🚨 OVERDUE" else Colors.YELLOW
                label = f" ({status})" if status != "✅ Taken" else ""
                if due_time:
                    print(f"      ➤ {med['medication']} — {med['dose']} at {due_time}{label}")
                else:
                    print(f"      ➤ {med['medication']} — {med['dose']}{label}")
                if med.get("notes"):
                    print(f"         📝 {med['notes']}")

        # Weights
        weights = pet.get("weights", [])
        if weights:
            last_weight = weights[-1]["weight"]
            print(f"   ⚖️  Last weight: {last_weight} kg ({len(weights)} logs)")

    print("="*50)

def plot_weekly_weight_trend(pets):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    plt.figure(figsize=(10, 6))
    for pet_name, pet in pets.items():
        weights = pet.get("weights", [])
        if not weights:
            continue
        dates = [datetime.strptime(w["timestamp"], "%Y-%m-%d %H:%M") for w in weights]
        values = [w["weight"] for w in weights]
        plt.plot(dates, values, marker="o", label=pet_name)

    plt.title("Weekly Weight Trend (kg)", fontsize=16)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Weight (kg)", fontsize=12)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def format_frequency_display(frequency, interval_hours, dosing_time):
    if frequency == "one_time":
        return "One-time"
    elif interval_hours:
        hours = interval_hours
        if hours == 24:
            return f"Daily at {dosing_time}" if dosing_time else "Every 24h"
        elif hours == 12:
            return f"Every 12h at {dosing_time}" if dosing_time else "Every 12h"
        else:
            return f"Every {hours}h"
    else:
        labels = {
            "every_day": "Daily",
            "every_3_days": "Every 3 days",
            "weekly": "Weekly"
        }
        return labels.get(frequency, frequency.replace('_', ' ').title())

def format_medication_status(med):
    """
    Returns a human-readable status for a medication entry:
    - ✅ Taken
    - 🚨 OVERDUE (if due time has passed and not taken)
    - ⏳ Upcoming (if due in future or today but not yet passed)
    - One-time (if no next_due)
    """
    next_due_str = med.get("next_due")
    taken = med.get("taken", False)
    dosing_time = med.get("dosing_time")

    if taken:
        return "✅ Taken"

    if not next_due_str:
        return "One-time"

    try:
        if " " in next_due_str:
            next_due = datetime.strptime(next_due_str, "%Y-%m-%d %H:%M")
        else:
            next_due = datetime.strptime(next_due_str, "%Y-%m-%d")
    except ValueError:
        return "Invalid date"

    now = datetime.now()

    # If due as a date only (no time), assume 00:00
    if " " not in next_due_str:
        next_due = next_due.replace(hour=0, minute=0, second=0, microsecond=0)

    if next_due < now:
        return "🚨 OVERDUE"
    else:
        return "⏳ Upcoming"

def view_upcoming_medications(pets):
    """
    Display ALL upcoming medication doses due within the next 7 days.
    Groups all doses by medication entry (not by dose).
    Shows count + list of dates per med.
    """
    print("\n" + "="*60)
    print(color_text("📅 UPCOMING MEDICATIONS (Next 7 Days)", Colors.BLUE + Colors.BOLD))
    print("="*60)

    found = False
    total_doses = 0
    today = datetime.now()
    end_date = today + timedelta(days=7)

    # Group meds by pet + medication + dose (to deduplicate identical entries)
    grouped = {}

    for pet_name, pet in pets.items():
        if not pet.get("medications"):
            continue

        for med in pet["medications"]:
            # Skip if no next_due
            next_due_str = med.get("next_due")
            if not next_due_str:
                continue

            # Derive interval in hours
            interval_hours = med.get("interval_hours")
            if not interval_hours:
                freq = med.get("frequency")
                if freq == "every_day":
                    interval_hours = 24
                elif freq == "every_3_days":
                    interval_hours = 72
                elif freq == "weekly":
                    interval_hours = 168
                else:
                    interval_hours = None

            # Generate all upcoming doses within next 7 days
            upcoming_doses = []
            try:
                if " " in next_due_str:
                    next_due = datetime.strptime(next_due_str, "%Y-%m-%d %H:%M")
                else:
                    next_due = datetime.strptime(next_due_str, "%Y-%m-%d")
            except ValueError:
                continue

            if next_due < today:
                continue

            if interval_hours is None:
                # One-time or unknown
                if today <= next_due <= end_date:
                    upcoming_doses.append(next_due)
            else:
                # Recurring: generate all doses until end_date
                current_due = next_due
                while current_due <= end_date:
                    upcoming_doses.append(current_due)
                    current_due += timedelta(hours=interval_hours)

            if not upcoming_doses:
                continue

            # Create a unique key for grouping: pet + med name + dose + frequency
            unique_key = (
                pet_name,
                med["medication"],
                med["dose"],
                med.get("frequency", "one_time"),
                med.get("interval_hours"),
                med.get("dosing_time")
            )

            if unique_key not in grouped:
                grouped[unique_key] = {
                    "pet": pet_name,
                    "med": med,
                    "doses": [],
                    "freq_display": format_frequency_display(
                        med.get("frequency"),
                        med.get("interval_hours"),
                        med.get("dosing_time")
                    ),
                    "status": format_medication_status(med)
                }

            grouped[unique_key]["doses"].extend(upcoming_doses)

    # Now print grouped results
    for key, group in grouped.items():
        med = group["med"]
        doses = group["doses"]
        pet_name = group["pet"]
        freq_display = group["freq_display"]
        status = group["status"]

        # Sort doses chronologically
        doses.sort()

        # Filter doses to only those within next 7 days (should already be, but just in case)
        doses = [d for d in doses if d >= today and d <= end_date]
        if not doses:
            continue

        found = True
        total_doses += len(doses)

        # Print main medication header
        print(color_text(f"  🐾 {pet_name} — {med['medication']} ({med['dose']})", Colors.GREEN))
        print(f"     ➤ Frequency: {freq_display} | {color_text(status, Colors.YELLOW if status == '⏳ Upcoming' else Colors.RED if status == '🚨 OVERDUE' else Colors.GREEN)}")
        print(f"     ➤ Upcoming doses: {len(doses)} total")

        # Print each upcoming dose in compact format
        for dose_time in doses:
            days_ahead = (dose_time.date() - today.date()).days
            if days_ahead == 0:
                day_str = "TODAY"
            elif days_ahead == 1:
                day_str = "TOMORROW"
            elif days_ahead <= 7:
                day_str = f"in {days_ahead} days"
            else:
                day_str = f"on {dose_time.strftime('%b %d')}"  # fallback

            print(f"        ➤ {day_str} — {dose_time.strftime('%Y-%m-%d %H:%M')}")

        if med.get("notes"):
            print(f"     ➤ Note: {med['notes']}")
        if med.get("reminder_enabled"):
            print(f"     ➤ 🔔 Reminder: ON")
        print()

    if not found:
        print(color_text("   🎯 No upcoming medications within 7 days.", Colors.YELLOW))
    else:
        print(color_text(f"\n✅ Total upcoming doses: {total_doses} in next 7 days", Colors.GREEN))

    print("="*60)
    input("Press Enter to return to main menu...")


# --- MANAGEMENT FUNCTIONS ---
def manage_medications(pets):
    """
    Full medication management menu with reorganized options:
    1. Add new medication
    2. View upcoming medications
    3. Mark medication as taken
    4. Edit notes on medication
    5. Delete medication entry
    0. Back to main menu
    """
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to manage medications for. Add a pet first." + Colors.RESET)
        return

    print("\n" + "="*60)
    print(color_text("💊 MANAGE MEDICATIONS", Colors.BLUE + Colors.BOLD))
    print("="*60)

    all_meds = []
    for pet_name, pet in pets.items():
        for i, med in enumerate(pet.get("medications", [])):
            all_meds.append({
                "pet": pet_name,
                "med": med,
                "id": i
            })

    if not all_meds:
        print(Colors.YELLOW + "⚠️  No medications set. Add one via Edit Pet." + Colors.RESET)
        # Offer to add one immediately
        add_new = input("Would you like to add a new medication now? (y/N): ").strip().lower()
        if add_new == 'y':
            # Reuse the "Add" logic from below
            pet_name = input("Enter pet name: ").strip()
            if pet_name not in pets:
                print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
                return
            medication = input("Medication name: ").strip()
            if not medication:
                print(Colors.RED + "❌ Medication name cannot be empty!" + Colors.RESET)
                return
            dose = input("Dose (e.g., 0.5ml): ").strip()
            if not dose:
                print(Colors.RED + "❌ Dose cannot be empty!" + Colors.RESET)
                return
            notes = input("📝 Optional notes: ").strip() or ""

            frequency = input("Frequency (one_time/every_day/every_3_days/weekly/custom): ").strip().lower()
            if frequency not in ["one_time", "every_day", "every_3_days", "weekly", "custom"]:
                frequency = "one_time"

            dosing_time = None
            interval_hours = None

            if frequency == "custom":
                try:
                    interval_hours = int(input("Interval in hours: "))
                    dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip()
                    if not dosing_time:
                        dosing_time = None
                except ValueError:
                    print(Colors.RED + "❌ Invalid interval." + Colors.RESET)
                    return
            elif frequency == "every_day":
                dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip() or None
                interval_hours = 24
            elif frequency == "every_3_days":
                dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip() or None
                interval_hours = 72
            elif frequency == "weekly":
                dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip() or None
                interval_hours = 168

            reminder_enabled = input("🔔 Enable reminder? (y/N): ").strip().lower() == 'y'

            next_due = None
            if frequency != "one_time":
                today_str = datetime.now().strftime("%Y-%m-%d")
                if dosing_time:
                    next_due = f"{today_str} {dosing_time}"
                else:
                    next_due = f"{today_str} 09:00"

            new_med = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "medication": medication,
                "dose": dose,
                "notes": notes,
                "frequency": frequency,
                "interval_hours": interval_hours,
                "dosing_time": dosing_time,
                "next_due": next_due,
                "reminder_enabled": reminder_enabled,
                "taken": False
            }

            pets[pet_name]["medications"].append(new_med)
            save_pets(pets)
            print(Colors.GREEN + "✅ Medication added!" + Colors.RESET)
        return

    # Show all meds with status
    print("All Medication Entries:")
    for item in all_meds:
        med = item["med"]
        next_due_str = med.get("next_due", "One-time")
        freq_display = format_frequency_display(
            med.get("frequency"),
            med.get("interval_hours"),
            med.get("dosing_time")
        )
        status = format_medication_status(med)
        color = Colors.GREEN if status == "✅ Taken" else Colors.RED if status == "🚨 OVERDUE" else Colors.YELLOW

        print(f"\n   [{item['id'] + 1}] {item['pet']} — {med['medication']} ({med['dose']})")
        print(f"      ➤ Due: {next_due_str} | {freq_display} | {color_text(status, color)}")
        if med.get("notes"):
            print(f"      ➤ Note: {med['notes']}")
        if med.get("reminder_enabled"):
            print(f"      ➤ 🔔 Reminder: ON")

    print("\n" + "🛠️  Options:")
    print("   1. Add new medication")
    print("   2. View upcoming medications")
    print("   3. Mark medication as taken")
    print("   4. Edit notes on medication")
    print("   5. Delete medication entry")
    print("   0. Back to main menu")
    print("-" * 60)

    choice = input("Choose an option (0-5): ").strip()

    if choice == "1":
        pet_name = input("Enter pet name: ").strip()
        if pet_name not in pets:
            print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
            return
        medication = input("Medication name: ").strip()
        if not medication:
            print(Colors.RED + "❌ Medication name cannot be empty!" + Colors.RESET)
            return
        dose = input("Dose (e.g., 0.5ml): ").strip()
        if not dose:
            print(Colors.RED + "❌ Dose cannot be empty!" + Colors.RESET)
            return
        notes = input("📝 Optional notes: ").strip() or ""

        frequency = input("Frequency (one_time/every_day/every_3_days/weekly/custom): ").strip().lower()
        if frequency not in ["one_time", "every_day", "every_3_days", "weekly", "custom"]:
            frequency = "one_time"

        dosing_time = None
        interval_hours = None

        if frequency == "custom":
            try:
                interval_hours = int(input("Interval in hours: "))
                dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip()
                if not dosing_time:
                    dosing_time = None
            except ValueError:
                print(Colors.RED + "❌ Invalid interval." + Colors.RESET)
                return
        elif frequency == "every_day":
            dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip() or None
            interval_hours = 24
        elif frequency == "every_3_days":
            dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip() or None
            interval_hours = 72
        elif frequency == "weekly":
            dosing_time = input("Dosing time (HH:MM, e.g., 08:00): ").strip() or None
            interval_hours = 168

        reminder_enabled = input("🔔 Enable reminder? (y/N): ").strip().lower() == 'y'

        next_due = None
        if frequency != "one_time":
            today_str = datetime.now().strftime("%Y-%m-%d")
            if dosing_time:
                next_due = f"{today_str} {dosing_time}"
            else:
                next_due = f"{today_str} 09:00"

        new_med = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "medication": medication,
            "dose": dose,
            "notes": notes,
            "frequency": frequency,
            "interval_hours": interval_hours,
            "dosing_time": dosing_time,
            "next_due": next_due,
            "reminder_enabled": reminder_enabled,
            "taken": False
        }

        pets[pet_name]["medications"].append(new_med)
        save_pets(pets)
        print(Colors.GREEN + "✅ Medication added!" + Colors.RESET)

    elif choice == "2":
        # Call the existing view function directly
        view_upcoming_medications(pets)

    elif choice == "3":
        try:
            idx = int(input("Enter number of medication to mark as taken: ")) - 1
            if idx < 0 or idx >= len(all_meds):
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
                return
            item = all_meds[idx]
            pet_name = item["pet"]
            med = item["med"]
            med["taken"] = True
            med["taken_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_pets(pets)
            print(Colors.GREEN + "✅ Marked as taken!" + Colors.RESET)
        except ValueError:
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "4":
        try:
            idx = int(input("Enter number of medication to edit notes: ")) - 1
            if idx < 0 or idx >= len(all_meds):
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
                return
            item = all_meds[idx]
            pet_name = item["pet"]
            med = item["med"]
            old_notes = med.get("notes", "")
            new_notes = input(f"Current notes: \"{old_notes}\"\nNew notes (leave blank to clear): ").strip()
            med["notes"] = new_notes
            save_pets(pets)
            print(Colors.GREEN + "✅ Notes updated!" + Colors.RESET)
        except ValueError:
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "5":
        try:
            idx = int(input("Enter number of medication to delete: ")) - 1
            if idx < 0 or idx >= len(all_meds):
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
                return
            item = all_meds[idx]
            pet_name = item["pet"]
            med = item["med"]
            pets[pet_name]["medications"].remove(med)
            save_pets(pets)
            print(Colors.GREEN + "✅ Medication deleted!" + Colors.RESET)
        except ValueError:
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "0":
        return
    else:
        print(Colors.RED + "❌ Invalid option. Please choose 0–5." + Colors.RESET)

    # Prompt to return after action
    input("\nPress Enter to return to main menu...")


def manage_feeding_schedule(pets):
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to set feeding schedule for. Add a pet first." + Colors.RESET)
        return

    print("\n" + "="*60)
    print(color_text("🍽️  SET FEEDING SCHEDULE", Colors.BLUE + Colors.BOLD))
    print("="*60)

    for i, pet_name in enumerate(pets.keys(), 1):
        print(f"{i}. {pet_name}")

    try:
        choice = int(input("Choose pet: ")) - 1
        pet_name = list(pets.keys())[choice]
    except (ValueError, IndexError):
        print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
        return

    pet = pets[pet_name]
    current_schedule = pet.get("feeding_schedule", [])
    current_reminders = pet.get("feeding_reminders", False)
    target_cal = pet.get("target_daily_calories")

    print(f"\nCurrent schedule: {current_schedule}")
    print(f"Current reminders: {'ON' if current_reminders else 'OFF'}")
    print(f"Target daily calories: {target_cal if target_cal is not None else 'Not set'} kcal")

    if target_cal is None:
        print(Colors.YELLOW + "⚠️  Target daily calories not set. Set weight first." + Colors.RESET)
        input("\nPress Enter to return...")
        return

    meals = input("Number of meals per day (1-4): ").strip()
    if not meals.isdigit() or not (1 <= int(meals) <= 4):
        print(Colors.RED + "❌ Must be 1-4 meals." + Colors.RESET)
        return
    meals = int(meals)

    # 🚨 NEW: Auto-split logic — healthy pattern
    schedule = []

    if meals == 1:
        # Single meal = 100%
        schedule = [target_cal]
        print(f"💡 Single meal: {target_cal:.1f} kcal")

    elif meals == 2:
        # Breakfast: 55%, Dinner: 45% (largest first, second largest last)
        schedule = [
            round(target_cal * 0.55, 2),
            round(target_cal * 0.45, 2)
        ]
        print(f"💡 Auto-split: Breakfast {schedule[0]:.1f} kcal, Dinner {schedule[1]:.1f} kcal")

    elif meals == 3:
        # Breakfast: 40%, Lunch: 30%, Dinner: 30%
        schedule = [
            round(target_cal * 0.40, 2),
            round(target_cal * 0.30, 2),
            round(target_cal * 0.30, 2)
        ]
        print(f"💡 Auto-split: Breakfast {schedule[0]:.1f} kcal, Lunch {schedule[1]:.1f} kcal, Dinner {schedule[2]:.1f} kcal")

    elif meals == 4:
        # Breakfast: 40%, Midday1: 20%, Midday2: 20%, Dinner: 20% → Wait! Dinner should be 30%
        # Correction: Dinner is second largest → 30%, so:
        # Breakfast: 40%, Midday1: 20%, Midday2: 10%, Dinner: 30% → No, that's uneven.
        # Better: Breakfast 40%, then split remaining 60% as 20%, 20%, 20% → but dinner should be larger than middle.
        # So: Breakfast 40%, Middle two: 15% each, Dinner 30% → 40+15+15+30 = 100 ✅
        schedule = [
            round(target_cal * 0.40, 2),
            round(target_cal * 0.15, 2),
            round(target_cal * 0.15, 2),
            round(target_cal * 0.30, 2)
        ]
        print(f"💡 Auto-split: Breakfast {schedule[0]:.1f} kcal, Snack1 {schedule[1]:.1f} kcal, Snack2 {schedule[2]:.1f} kcal, Dinner {schedule[3]:.1f} kcal")

    # ✅ Now present auto-split as default, but let user override
    print(f"\nAuto-calculated schedule: {schedule} kcal")
    confirm = input("✅ Accept this distribution? (y/N): ").strip().lower()

    if confirm == 'y':
        # Use auto-split
        pass  # schedule already set
    else:
        # Let user override — but still enforce: only last meal can be left blank (for auto-fill)
        print(f"\nEdit calories manually. Enter values or leave blank to accept auto-split.")
        print(f"   (Only last meal can be left blank — it will auto-fill with remainder.)")
        schedule = []
        remaining = target_cal

        for i in range(meals):
            if i == meals - 1:
                # Last meal: can be blank → auto-fill
                prompt = f"Meal {i+1} calories (leave blank to auto-fill with {remaining:.1f}): "
            else:
                prompt = f"Meal {i+1} calories (default: {schedule[i] if i < len(schedule) else 'auto'} kcal): "

            cal_input = input(prompt).strip()

            if cal_input == "" and i == meals - 1:
                # Last meal blank → use remaining
                schedule.append(remaining)
                remaining = 0
            elif cal_input == "" and i < meals - 1:
                # Not last meal, blank → use default auto-split value
                if i < len(schedule):  # safety
                    schedule.append(schedule[i])  # use original auto value
                else:
                    # This shouldn't happen — use default pattern
                    default_vals = {
                        1: [target_cal],
                        2: [round(target_cal * 0.55, 2), round(target_cal * 0.45, 2)],
                        3: [round(target_cal * 0.40, 2), round(target_cal * 0.30, 2), round(target_cal * 0.30, 2)],
                        4: [round(target_cal * 0.40, 2), round(target_cal * 0.15, 2), round(target_cal * 0.15, 2), round(target_cal * 0.30, 2)]
                    }
                    schedule.append(default_vals[meals][i])
                remaining -= schedule[i]
            else:
                try:
                    cal = float(cal_input)
                    if cal < 0:
                        print(Colors.RED + "❌ Calories must be positive." + Colors.RESET)
                        return
                    schedule.append(cal)
                    remaining -= cal
                except ValueError:
                    print(Colors.RED + "❌ Invalid number." + Colors.RESET)
                    return

        # Validate remaining
        if remaining < 0:
            print(Colors.RED + "❌ Total entered exceeds target calories." + Colors.RESET)
            return
        elif remaining > 0 and meals > 1:  # if last meal was NOT blank, warn
            print(Colors.YELLOW + f"⚠️  {remaining:.1f} kcal unassigned — consider increasing last meal." + Colors.RESET)

    # Final validation
    total = sum(schedule)
    if abs(total - target_cal) > 0.1:
        print(Colors.YELLOW + f"⚠️  Total ({total:.1f} kcal) ≠ Target ({target_cal} kcal). Adjusted." + Colors.RESET)

    # Ask for reminders
    reminder = input("🔔 Enable feeding reminders? (y/N): ").strip().lower() == 'y'

    # Save
    pet["feeding_schedule"] = schedule
    pet["feeding_reminders"] = reminder
    save_pets(pets)

    # Display final
    display_schedule = [f"{cal:.1f}" for cal in schedule]
    print(Colors.GREEN + f"✅ Feeding schedule set: [{', '.join(display_schedule)}] kcal" + Colors.RESET)
    print(f"   Reminders: {'ON' if reminder else 'OFF'}")


def manage_feeding(pets):
    """
    Sub-menu for feeding: View, Set, or Delete schedule.
    """
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets available. Add a pet first." + Colors.RESET)
        input("\nPress Enter to return...")
        return

    while True:
        print("\n" + "="*50)
        print(color_text("🍽️  MANAGE FEEDING", Colors.BLUE + Colors.BOLD))
        print("="*50)
        print("1. View Feeding Schedule")
        print("2. Set Feeding Schedule")
        print("3. Delete Feeding Schedule")  # ✅ NEW OPTION
        print("0. Back to Settings")
        print("-" * 50)
        choice = input("Choose option: ").strip()

        if choice == "1":
            view_feeding_schedule(pets)
        elif choice == "2":
            manage_feeding_schedule(pets)
        elif choice == "3":
            delete_feeding_schedule(pets)  # ✅ NEW FUNCTION
        elif choice == "0":
            break
        else:
            print(Colors.RED + "❌ Invalid option." + Colors.RESET)

def delete_feeding_schedule(pets):
    """
    Deletes the feeding schedule and reminders for a selected pet.
    """
    pet_name = select_pet(pets)
    if not pet_name:
        return

    pet = pets[pet_name]
    schedule = pet.get("feeding_schedule", [])
    reminders = pet.get("feeding_reminders", False)

    if not schedule and not reminders:
        print(Colors.YELLOW + f"⚠️  No feeding schedule set for {pet_name}." + Colors.RESET)
        return

    print(f"\n⚠️  You are about to delete the feeding schedule for {pet_name}:")
    if schedule:
        print(f"   Schedule: {schedule} kcal")
    if reminders:
        print(f"   Reminders: ON")

    confirm = input("\nAre you SURE you want to delete this? (y/N): ").strip().lower()

    if confirm == 'y':
        pet["feeding_schedule"] = []
        pet["feeding_reminders"] = False
        save_pets(pets)
        print(Colors.GREEN + f"✅ Feeding schedule and reminders deleted for {pet_name}." + Colors.RESET)
    else:
        print(Colors.YELLOW + "❌ Deletion cancelled." + Colors.RESET)

def view_feeding_schedule(pets):
    """
    Displays current feeding schedule for selected pet.
    Shows: meals per day, calorie distribution, reminders, target.
    """
    pet_name = select_pet(pets)
    if not pet_name:
        return

    pet = pets[pet_name]
    schedule = pet.get("feeding_schedule", [])
    reminders = pet.get("feeding_reminders", False)
    target_cal = pet.get("target_daily_calories")

    print("\n" + "="*50)
    print(color_text(f"🍽️  FEEDING SCHEDULE FOR {pet_name.upper()}", Colors.CYAN + Colors.BOLD))
    print("="*50)

    if not schedule:
        print("   🚫 No feeding schedule set. Use 'Set Feeding Schedule' to define meals.")
    else:
        print(f"   🍽️  Meals per day: {len(schedule)}")
        try:
            total = sum(float(cal) for cal in schedule)
            print(f"   📊 Calorie distribution: {' + '.join(str(round(float(cal), 2)) for cal in schedule)} kcal")
            print(f"   📈 Total daily calories: {total:.1f} kcal")
        except (ValueError, TypeError):
            print("   📊 Calorie distribution: (invalid data)")
            print("   📈 Total daily calories: 0.0 kcal")

    if target_cal is not None:
        print(f"   🎯 Target daily calories: {target_cal} kcal")
        try:
            total = sum(float(cal) for cal in schedule)
            if abs(total - target_cal) > 1:
                print(f"   ⚠️  Warning: Schedule ({total:.1f} kcal) ≠ Target ({target_cal} kcal)")
        except (ValueError, TypeError):
            pass  # Skip if schedule is invalid

    print(f"   🔔 Feeding reminders: {'ON' if reminders else 'OFF'}")

    print("="*50)
    input("Press Enter to return...")


def change_weight_unit():
    prefs = load_user_prefs()
    current = prefs.get("unit", "kg")
    print(f"Current unit: {current.upper()}")
    new = input("Change to (kg/lb): ").strip().lower()
    if new in ["kg", "lb"]:
        prefs["unit"] = new
        save_user_prefs(prefs)
        print(Colors.GREEN + f"✅ Weight unit changed to {new.upper()}!" + Colors.RESET)
    else:
        print(Colors.RED + "❌ Must be 'kg' or 'lb'." + Colors.RESET)

def delete_all_data():
    confirm = input("⚠️  Are you SURE you want to delete ALL data (pets, logs, prefs)? (y/N): ").strip().lower()
    if confirm != 'y':
        print(Colors.YELLOW + "❌ Deletion cancelled." + Colors.RESET)
        return
    files = [PETS_FILE, LOGS_FILE, USER_PREFS_FILE]
    for f in files:
        if os.path.exists(f):
            os.remove(f)
    print(Colors.GREEN + "✅ All data deleted!" + Colors.RESET)

def reset_user_prefs():
    confirm = input("⚠️  Reset user preferences to default? (y/N): ").strip().lower()
    if confirm != 'y':
        print(Colors.YELLOW + "❌ Reset cancelled." + Colors.RESET)
        return
    save_user_prefs({"unit": "kg"})
    print(Colors.GREEN + "✅ Preferences reset to default (kg)." + Colors.RESET)

def export_logs_to_csv(pets, filename):
    import csv
    os.makedirs("exports", exist_ok=True)
    with open(f"exports/{filename}", 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Pet", "Type", "Timestamp", "Details"])
        for pet_name, pet in pets.items():
            for log in pet.get("feedings", []):
                writer.writerow([pet_name, "Feeding", log["time"], f"{log['grams']}g ({log['calories']} kcal)"])
            for log in pet.get("medications", []):
                taken = "✅ Taken" if log.get("taken") else "❌ Not taken"
                writer.writerow([pet_name, "Medication", log["timestamp"], f"{log['medication']} {log['dose']} - {taken}"])
            for log in pet.get("weights", []):
                writer.writerow([pet_name, "Weight", log["timestamp"], f"{log['weight']} kg"])
    print(Colors.GREEN + f"✅ Logs exported to exports/{filename}" + Colors.RESET)

def export_logs_to_json(pets, filename):
    import json
    os.makedirs("exports", exist_ok=True)
    export_data = {}
    for pet_name, pet in pets.items():
        export_data[pet_name] = {
            "feedings": pet.get("feedings", []),
            "medications": pet.get("medications", []),
            "weights": pet.get("weights", [])
        }
    with open(f"exports/{filename}", 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    print(Colors.GREEN + f"✅ Logs exported to exports/{filename}" + Colors.RESET)

# --- BONUS: Helper to format time for display ---
def format_time_for_display(time_str):
    """Convert 'YYYY-MM-DD HH:MM:SS' to 'MMM D, h:mm A' (e.g., Apr 5, 8:30 AM)"""
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %I:%M %p").replace(" 0", " ")  # Remove leading zero
    except:
        return time_str