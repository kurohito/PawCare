import json
import os
from datetime import datetime, timedelta

from .colors import Colors, color_text

PETS_FILE = "data/pets.json"
USER_PREFS_FILE = "data/user_prefs.json"
LOGS_FILE = "data/logs.json"
ACTION_LOG = "data/action.log"

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def ensure_data_directory():
    """Ensure the data directory exists for file storage."""
    if not os.path.exists("data"):
        os.makedirs("data")
        print(color_text("ℹ️  Created 'data' directory for storage.", Colors.CYAN))


def load_pets():
    """Load pet data from pets.json. Returns empty dict if file doesn't exist or is corrupt."""
    ensure_data_directory()

    if not os.path.exists(PETS_FILE):
        return {}
    try:
        with open(PETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for pet_name in data:
                pet = data[pet_name]
                if "weight" not in pet:
                    pet["weight"] = None
                if "target_daily_calories" not in pet:
                    pet["target_daily_calories"] = None
                if "species" not in pet:
                    pet["species"] = None
                if "medications" not in pet:
                    pet["medications"] = []
                if "feeding_schedule" not in pet:
                    pet["feeding_schedule"] = []
                if "feeding_reminders" not in pet:
                    pet["feeding_reminders"] = False
                if "weights" not in pet:
                    pet["weights"] = []
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        print(color_text("⚠️  Corrupted pets.json. Starting fresh.", Colors.YELLOW))
        return {}


def save_pets(pets):
    """Save pet data to pets.json."""
    ensure_data_directory()
    with open(PETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pets, f, indent=4, ensure_ascii=False)


def load_user_prefs():
    """Load user preferences (e.g., weight unit). Returns default if file missing or corrupt."""
    ensure_data_directory()
    if not os.path.exists(USER_PREFS_FILE):
        return {"unit": "kg"}
    try:
        with open(USER_PREFS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(color_text("⚠️  Corrupted user_prefs.json. Resetting to default.", Colors.YELLOW))
        return {"unit": "kg"}


def save_user_prefs(prefs):
    """Save user preferences to user_prefs.json."""
    ensure_data_directory()
    with open(USER_PREFS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prefs, f, indent=4, ensure_ascii=False)


def log_feeding_entry(pets, pet_name, grams, calories):
    """Log a feeding entry for a pet."""
    if pet_name not in pets:
        print(color_text("❌ Pet not found!", Colors.RED))
        return

    if "feedings" not in pets[pet_name]:
        pets[pet_name]["feedings"] = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    pets[pet_name]["feedings"].append({
        "timestamp": now,
        "grams": grams,
        "calories": calories
    })

    save_pets(pets)
    print(color_text(f"✅ Logged: {grams}g ({calories} kcal) at {now}", Colors.GREEN))


def log_weight_entry(pets, pet_name, weight):
    """Log a weight entry for a pet."""
    if pet_name not in pets:
        print(color_text("❌ Pet not found!", Colors.RED))
        return

    if "weights" not in pets[pet_name]:
        pets[pet_name]["weights"] = []

    now = datetime.now().strftime("%Y-%m-%d")
    pets[pet_name]["weights"].append({
        "date": now,
        "weight": weight
    })

    pets[pet_name]["weight"] = weight
    save_pets(pets)
    print(color_text(f"✅ Logged weight: {weight} kg on {now}", Colors.GREEN))


def format_frequency_display(frequency, interval_hours, dosing_time):
    """
    Helper function to generate human-readable frequency display.
    Returns a string like: "Every 12h at 14:00", "Daily at 08:00", "One-time"
    """
    if frequency == "one_time":
        return "One-time"
    elif interval_hours is not None:
        base = f"Every {interval_hours}h"
        return f"{base} at {dosing_time}" if dosing_time else base
    else:
        freq_labels = {
            "every_day": "Daily",
            "every_3_days": "Every 3 days",
            "weekly": "Weekly"
        }
        base = freq_labels.get(frequency, frequency.replace("_", " ").title())
        return f"{base} at {dosing_time}" if dosing_time else base


def log_medication_entry(pets, pet_name, medication, dose, notes=""):
    """Log a medication entry with scheduling and reminders."""
    if pet_name not in pets:
        print(color_text("❌ Pet not found!", Colors.RED))
        return

    if "medications" not in pets[pet_name]:
        pets[pet_name]["medications"] = []

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\n📌 How often should this medication be given?")
    print("  1. One-time only")
    print("  2. Daily (every 24 hours)")
    print("  3. Every 3 days")
    print("  4. Weekly")
    print("  5. Custom interval (e.g., every 8 hours)")
    while True:
        choice = input("Choose 1-5: ").strip()
        if choice == "1":
            frequency = "one_time"
            interval_hours = None
            next_due = None
            dosing_time = None
            break
        elif choice == "2":
            frequency = "every_day"
            interval_hours = 24
            break
        elif choice == "3":
            frequency = "every_3_days"
            interval_hours = 72
            break
        elif choice == "4":
            frequency = "weekly"
            interval_hours = 168
            break
        elif choice == "5":
            while True:
                try:
                    hours = int(input("Enter interval in hours (e.g., 8): ").strip())
                    if hours <= 0:
                        print(color_text("❌ Interval must be positive.", Colors.RED))
                        continue
                    frequency = "custom"
                    interval_hours = hours
                    break
                except ValueError:
                    print(color_text("❌ Please enter a valid number of hours.", Colors.RED))
            break
        else:
            print(color_text("❌ Invalid choice. Choose 1–5.", Colors.RED))

    dosing_time = None
    if frequency != "one_time":
        print("\n⏰ What time of day should this dose be given? (24-hour format, e.g., 08:00)")
        while True:
            time_input = input("Time (HH:MM): ").strip()
            if len(time_input) == 5 and time_input[2] == ":":
                try:
                    h, m = map(int, time_input.split(":"))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        dosing_time = f"{h:02d}:{m:02d}"
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print(color_text("❌ Invalid time. Use HH:MM (e.g., 08:30).", Colors.RED))
            else:
                print(color_text("❌ Invalid format. Use HH:MM (e.g., 08:30).", Colors.RED))

    if frequency == "one_time":
        next_due = None
    elif dosing_time:
        first_due_str = f"{now.split()[0]} {dosing_time}"
        first_due = datetime.strptime(first_due_str, "%Y-%m-%d %H:%M")
        if first_due < datetime.now():
            first_due += timedelta(days=1)
        next_due = first_due.strftime("%Y-%m-%d %H:%M")
    else:
        if interval_hours:
            next_due = (datetime.now() + timedelta(hours=interval_hours)).strftime("%Y-%m-%d %H:%M")
        else:
            if frequency == "every_day":
                next_due = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            elif frequency == "every_3_days":
                next_due = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
            elif frequency == "weekly":
                next_due = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d")

    remind_choice = input("\n🔔 Enable reminder for this medication? (y/N): ").strip().lower()
    reminder_enabled = remind_choice in ['y', 'yes']

    pets[pet_name]["medications"].append({
        "timestamp": now,
        "medication": medication,
        "dose": dose,
        "notes": notes,
        "frequency": frequency,
        "interval_hours": interval_hours,
        "dosing_time": dosing_time,
        "next_due": next_due,
        "reminder_enabled": reminder_enabled
    })

    save_pets(pets)
    note_part = f" | {notes}" if notes else ""
    print(color_text(f"✅ Logged medication: {medication} — {dose}{note_part} at {now}", Colors.GREEN))
    if next_due:
        print(color_text(f"   👉 Next dose due: {next_due}", Colors.CYAN))
    if reminder_enabled:
        print(color_text("   👉 🔔 Reminder: ON", Colors.CYAN))


def view_upcoming_medications(pets):
    """
    Display ALL upcoming medication doses due within the next 7 days.
    For recurring meds (e.g., every 24h), generates and shows ALL doses in the window.
    """
    print("\n" + "="*60)
    print(color_text("📅 UPCOMING MEDICATIONS (Next 7 Days)", Colors.BLUE + Colors.BOLD))
    print("="*60)

    found = False
    total_doses = 0
    today = datetime.now()
    end_date = today + timedelta(days=7)

    for pet_name, pet in pets.items():
        if not pet.get("medications"):
            continue

        for med in pet["medications"]:
            next_due_str = med.get("next_due")
            if not next_due_str:
                continue

            try:
                if " " in next_due_str:
                    next_due = datetime.strptime(next_due_str, "%Y-%m-%d %H:%M")
                else:
                    next_due = datetime.strptime(next_due_str, "%Y-%m-%d")
            except ValueError:
                continue

            if next_due < today:
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

            upcoming_doses = []
            current_due = next_due

            if interval_hours is None:
                # One-time or unknown interval
                if today <= current_due <= end_date:
                    upcoming_doses.append(current_due)
            else:
                # Recurring: generate all doses until end_date
                while current_due <= end_date:
                    upcoming_doses.append(current_due)
                    current_due += timedelta(hours=interval_hours)

            if upcoming_doses:
                found = True
                total_doses += len(upcoming_doses)

                freq_display = format_frequency_display(
                    med.get("frequency"),
                    med.get("interval_hours"),
                    med.get("dosing_time")
                )

                for dose_time in upcoming_doses:
                    days_ahead = (dose_time.date() - today.date()).days
                    if days_ahead == 0:
                        day_str = "TODAY"
                    elif days_ahead == 1:
                        day_str = "TOMORROW"
                    else:
                        day_str = f"in {days_ahead} days"

                    print(color_text(f"  🐾 {pet_name} — {med['medication']}", Colors.GREEN))
                    print(f"     ➤ Dose: {med['dose']}")
                    print(f"     ➤ Due: {dose_time.strftime('%Y-%m-%d %H:%M')} ({day_str}) | {freq_display}")
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


def print_daily_summary(pets):
    print("\n" + "="*70)
    print(color_text("🌞 DAILY PET SUMMARY", Colors.YELLOW + Colors.BOLD))
    print("="*70)

    if not pets:
        print(color_text("   🐾 No pets registered yet.", Colors.YELLOW))
        print("="*70)
        input("Press Enter to return...")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    today_time = datetime.now().strftime("%H:%M")

    prefs = load_user_prefs()
    unit = prefs.get("unit", "kg")
    unit_symbol = "kg" if unit == "kg" else "lb"

    for pet_name, pet in pets.items():
        print(f"\n{Colors.BOLD}{pet_name.upper()}{Colors.RESET}")
        print("-" * 50)

        feedings_today = []
        if "feedings" in pet:
            feedings_today = [
                f for f in pet["feedings"] 
                if f["timestamp"].startswith(today_str)
            ]
        
        if feedings_today:
            total_grams = sum(f["grams"] for f in feedings_today)
            total_calories = sum(f["calories"] for f in feedings_today)
            print(color_text(f"   🍽️  Today's feedings: {len(feedings_today)} meals ({total_grams}g, {total_calories} kcal)", Colors.GREEN))
            for f in feedings_today:
                time = f["timestamp"].split(" ")[1]
                print(f"      ➤ {time} — {f['grams']}g ({f['calories']} kcal)")
        else:
            print(color_text("   🍽️  No feedings logged today.", Colors.YELLOW))

        if pet["weight"] is not None:
            current_weight = pet["weight"]
            if unit == "lb":
                current_weight = round(current_weight * 2.20462, 2)
            print(color_text(f"   ⚖️  Current weight: {current_weight} {unit_symbol}", Colors.CYAN))
        else:
            print(color_text("   ⚖️  Weight not logged yet.", Colors.YELLOW))

        meds_today = []
        if "medications" in pet:
            for med in pet["medications"]:
                next_due = med.get("next_due")
                if next_due and next_due.startswith(today_str):
                    meds_today.append(med)

        if meds_today:
            print(color_text(f"   💊 Medications due TODAY:", Colors.RED))
            for med in meds_today:
                due_time = med.get("dosing_time", "")
                if due_time:
                    print(f"      ➤ {med['medication']} — {med['dose']} at {due_time}")
                else:
                    print(f"      ➤ {med['medication']} — {med['dose']}")
                if med.get("notes"):
                    print(f"         📝 {med['notes']}")
        else:
            print(color_text("   💊 No medications due today.", Colors.YELLOW))

        schedule = pet.get("feeding_schedule", [])
        reminders = pet.get("feeding_reminders", False)
        if schedule:
            schedule_str = " | ".join(schedule)
            if reminders:
                print(color_text(f"   🕒 Scheduled meals: {schedule_str} (Reminders ON)", Colors.MAGENTA))
            else:
                print(f"   🕒 Scheduled meals: {schedule_str} (Reminders OFF)")
        else:
            print(color_text("   🕒 No feeding schedule set.", Colors.YELLOW))

        target_cal = pet.get("target_daily_calories")
        if target_cal is not None:
            total_today = sum(f["calories"] for f in feedings_today)
            progress = (total_today / target_cal) * 100 if target_cal > 0 else 0
            bar = "█" * int(progress // 10) + "░" * (10 - int(progress // 10))
            print(f"   🎯 Target: {target_cal} kcal | {int(progress)}% {bar}")
        else:
            print(color_text("   🎯 Target calories: Not set. Use Settings → Set Feeding Schedule.", Colors.YELLOW))

    print("="*70)
    input("Press Enter to return to main menu...")


def plot_weekly_weight_trend(pets):
    print("\n" + "="*60)
    print(color_text("📈 WEEKLY WEIGHT TREND", Colors.GREEN + Colors.BOLD))
    print("="*60)

    if not pets:
        print(color_text("   🐾 No pets registered.", Colors.YELLOW))
        print("="*60)
        input("Press Enter to return...")
        return

    prefs = load_user_prefs()
    unit = prefs.get("unit", "kg")
    unit_symbol = "kg" if unit == "kg" else "lb"

    if not MATPLOTLIB_AVAILABLE:
        print(color_text("⚠️  matplotlib is not installed. Installing it is recommended for charts.", Colors.YELLOW))
        print("   Run this command in your terminal to install it:")
        print(f"     {color_text('pip install matplotlib', Colors.CYAN)}")
        print("\nHere's a text-based trend instead:")
        print("-" * 50)

        for pet_name, pet in pets.items():
            weights = pet.get("weights", [])
            if not weights:
                print(f"   🐾 {pet_name}: No weight data logged.")
                continue

            weights.sort(key=lambda x: x["date"], reverse=True)
            latest_7 = weights[:7]
            latest_7.reverse()

            print(f"\n   🐾 {pet_name}:")
            for entry in latest_7:
                date = entry["date"]
                w = entry["weight"]
                if unit == "lb":
                    w = round(w * 2.20462, 2)
                print(f"      {date}: {w} {unit_symbol}")

        print("-" * 50)
        input("Press Enter to return...")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink']
    color_map = {}

    for idx, (pet_name, pet) in enumerate(pets.items()):
        weights = pet.get("weights", [])
        if not weights:
            continue

        weights.sort(key=lambda x: x["date"])
        dates = [datetime.strptime(entry["date"], "%Y-%m-%d") for entry in weights]
        values = [entry["weight"] for entry in weights]

        if unit == "lb":
            values = [round(w * 2.20462, 2) for w in values]

        color = colors[idx % len(colors)]
        color_map[pet_name] = color

        ax.plot(dates, values, marker='o', label=pet_name, color=color, linewidth=2, markersize=6)

    ax.set_title(f"🐾 Weekly Weight Trend ({unit_symbol})", fontsize=16, fontweight='bold')
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel(f"Weight ({unit_symbol})", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(title="Pets", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("weekly_weight_trend.png", dpi=150, bbox_inches='tight')
    print(color_text(f"✅ Chart saved as 'weekly_weight_trend.png' ({unit_symbol})", Colors.CYAN))
    plt.show()

    print("="*60)
    input("Press Enter to return to main menu...")


def manage_medications(pets):
    print("\n" + "="*60)
    print(color_text("💊 MANAGE MEDICATIONS", Colors.MAGENTA + Colors.BOLD))
    print("="*60)

    if not pets:
        print(color_text("   🐾 No pets registered.", Colors.YELLOW))
        print("="*60)
        input("Press Enter to return...")
        return

    all_meds = []
    for pet_name, pet in pets.items():
        for idx, med in enumerate(pet["medications"]):
            all_meds.append({
                "pet": pet_name,
                "index": idx,
                "med": med,
                "id": len(all_meds) + 1
            })

    if all_meds:
        print(f"\n{Colors.UNDERLINE}All Medication Entries:{Colors.RESET}")
        for item in all_meds:
            med = item["med"]
            due = med.get("next_due", "One-time")
            status = "✅ Taken" if med.get("taken") else "⏳ Due"
            color = Colors.GREEN if med.get("taken") else Colors.YELLOW

            freq_display = format_frequency_display(
                med.get("frequency"),
                med.get("interval_hours"),
                med.get("dosing_time")
            )

            print(f"   [{item['id']}] {item['pet']} — {med['medication']} ({med['dose']})")
            print(f"      ➤ Due: {due} | {freq_display} | {color_text(status, color)}")
            if med.get("notes"):
                print(f"      ➤ Note: {med['notes']}")
            if med.get("reminder_enabled"):
                print(f"      ➤ 🔔 Reminder: ON")
            print()
    else:
        print(color_text("   🚫 No medications logged yet.", Colors.YELLOW))

    while True:
        print("\n🛠️  Options:")
        print("   1. Mark medication as taken")
        print("   2. Delete medication entry")
        print("   3. Edit notes")
        print("   4. Add new medication")
        print("   0. Back to main menu")
        choice = input("Choose an option (0-4): ").strip()

        if choice == "0":
            break

        elif choice == "1":
            try:
                med_id = int(input("Enter the ID of the medication to mark as taken: ").strip())
                target = next((item for item in all_meds if item["id"] == med_id), None)
                if not target:
                    print(color_text("❌ Invalid ID.", Colors.RED))
                    continue

                pet_name = target["pet"]
                med_idx = target["index"]
                med = pets[pet_name]["medications"][med_idx]

                med["taken"] = True
                med["taken_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                if med.get("interval_hours"):
                    interval = med["interval_hours"]
                    if med.get("dosing_time"):
                        now = datetime.now()
                        next_time_str = med["dosing_time"]
                        next_date = (now + timedelta(hours=interval)).strftime("%Y-%m-%d")
                        med["next_due"] = f"{next_date} {next_time_str}"
                    else:
                        med["next_due"] = (now + timedelta(hours=interval)).strftime("%Y-%m-%d %H:%M")
                else:
                    freq = med.get("frequency", "")
                    if freq == "every_day":
                        if med.get("dosing_time"):
                            now = datetime.now()
                            next_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
                            med["next_due"] = f"{next_date} {med['dosing_time']}"
                        else:
                            med["next_due"] = (now + timedelta(days=1)).strftime("%Y-%m-%d")
                    elif freq == "every_3_days":
                        med["next_due"] = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
                    elif freq == "weekly":
                        med["next_due"] = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d")

                save_pets(pets)
                print(color_text(f"✅ Marked '{med['medication']}' as taken!", Colors.GREEN))
                if med["next_due"]:
                    print(f"   👉 Next due: {med['next_due']}")

            except (ValueError, IndexError):
                print(color_text("❌ Invalid input.", Colors.RED))

        elif choice == "2":
            try:
                med_id = int(input("Enter the ID of the medication to delete: ").strip())
                target = next((item for item in all_meds if item["id"] == med_id), None)
                if not target:
                    print(color_text("❌ Invalid ID.", Colors.RED))
                    continue

                pet_name = target["pet"]
                med_idx = target["index"]
                med_name = pets[pet_name]["medications"][med_idx]["medication"]
                confirm = input(f"⚠️  Delete '{med_name}'? (y/N): ").strip().lower()
                if confirm == "y":
                    del pets[pet_name]["medications"][med_idx]
                    save_pets(pets)
                    print(color_text(f"🗑️  Deleted '{med_name}'.", Colors.RED))
                else:
                    print("Operation cancelled.")

            except (ValueError, IndexError):
                print(color_text("❌ Invalid input.", Colors.RED))

        elif choice == "3":
            try:
                med_id = int(input("Enter the ID of the medication to edit: ").strip())
                target = next((item for item in all_meds if item["id"] == med_id), None)
                if not target:
                    print(color_text("❌ Invalid ID.", Colors.RED))
                    continue

                pet_name = target["pet"]
                med_idx = target["index"]
                current_notes = pets[pet_name]["medications"][med_idx].get("notes", "")

                print(f"Current notes: {current_notes or '(none)'}")
                new_notes = input("Enter new notes (or press Enter to skip): ").strip()
                if new_notes:
                    pets[pet_name]["medications"][med_idx]["notes"] = new_notes
                    save_pets(pets)
                    print(color_text("✅ Notes updated!", Colors.GREEN))

            except (ValueError, IndexError):
                print(color_text("❌ Invalid input.", Colors.RED))

        elif choice == "4":
            print("\n" + "="*40)
            print(color_text("➕ ADD NEW MEDICATION", Colors.CYAN + Colors.BOLD))
            print("="*40)

            print("Which pet needs a new medication?")
            pet_names = list(pets.keys())
            for i, name in enumerate(pet_names, 1):
                print(f"   {i}. {name}")
            print("   0. Cancel")

            try:
                pet_choice = int(input("Choose pet (0 to cancel): ").strip())
                if pet_choice == 0:
                    continue
                if pet_choice < 1 or pet_choice > len(pet_names):
                    print(color_text("❌ Invalid choice.", Colors.RED))
                    continue
                pet_name = pet_names[pet_choice - 1]
            except ValueError:
                print(color_text("❌ Invalid input.", Colors.RED))
                continue

            medication = input("💊 Medication name (e.g., 'Gabapentin'): ").strip()
            if not medication:
                print(color_text("❌ Medication name cannot be empty.", Colors.RED))
                continue

            dose = input("💊 Dose (e.g., '1 tablet', '0.5 mL'): ").strip()
            if not dose:
                print(color_text("❌ Dose cannot be empty.", Colors.RED))
                continue

            notes = input("📝 Optional notes (press Enter to skip): ").strip() or ""

            print("\n📌 How often should this medication be given?")
            print("   1. One-time only")
            print("   2. Daily (every 24 hours)")
            print("   3. Every 3 days")
            print("   4. Weekly")
            print("   5. Custom interval (e.g., every 8 hours)")
            while True:
                freq_choice = input("Choose 1-5: ").strip()
                if freq_choice == "1":
                    frequency = "one_time"
                    interval_hours = None
                    next_due = None
                    dosing_time = None
                    break
                elif freq_choice == "2":
                    frequency = "every_day"
                    interval_hours = 24
                    break
                elif freq_choice == "3":
                    frequency = "every_3_days"
                    interval_hours = 72
                    break
                elif freq_choice == "4":
                    frequency = "weekly"
                    interval_hours = 168
                    break
                elif freq_choice == "5":
                    while True:
                        try:
                            hours = int(input("Enter interval in hours (e.g., 8): ").strip())
                            if hours <= 0:
                                print(color_text("❌ Interval must be positive.", Colors.RED))
                                continue
                            frequency = "custom"
                            interval_hours = hours
                            break
                        except ValueError:
                            print(color_text("❌ Please enter a valid number of hours.", Colors.RED))
                    break
                else:
                    print(color_text("❌ Invalid choice. Choose 1–5.", Colors.RED))

            dosing_time = None
            if frequency != "one_time":
                print("\n⏰ What time of day should this dose be given? (24-hour format, e.g., 08:00)")
                while True:
                    time_input = input("Time (HH:MM): ").strip()
                    if len(time_input) == 5 and time_input[2] == ":":
                        try:
                            h, m = map(int, time_input.split(":"))
                            if 0 <= h <= 23 and 0 <= m <= 59:
                                dosing_time = f"{h:02d}:{m:02d}"
                                break
                            else:
                                raise ValueError
                        except ValueError:
                            print(color_text("❌ Invalid time. Use HH:MM (e.g., 08:30).", Colors.RED))
                    else:
                        print(color_text("❌ Invalid format. Use HH:MM (e.g., 08:30).", Colors.RED))

            now = datetime.now()
            if frequency == "one_time":
                next_due = None
            elif dosing_time:
                first_due_str = f"{now.strftime('%Y-%m-%d')} {dosing_time}"
                first_due = datetime.strptime(first_due_str, "%Y-%m-%d %H:%M")
                if first_due < now:
                    first_due += timedelta(days=1)
                next_due = first_due.strftime("%Y-%m-%d %H:%M")
            else:
                if interval_hours:
                    next_due = (now + timedelta(hours=interval_hours)).strftime("%Y-%m-%d %H:%M")
                else:
                    if frequency == "every_day":
                        next_due = (now + timedelta(days=1)).strftime("%Y-%m-%d")
                    elif frequency == "every_3_days":
                        next_due = (now + timedelta(days=3)).strftime("%Y-%m-%d")
                    elif frequency == "weekly":
                        next_due = (now + timedelta(weeks=1)).strftime("%Y-%m-%d")

            remind_choice = input("\n🔔 Enable reminder for this medication? (y/N): ").strip().lower()
            reminder_enabled = remind_choice in ['y', 'yes']

            timestamp = now.strftime("%Y-%m-%d %H:%M")

            if "medications" not in pets[pet_name]:
                pets[pet_name]["medications"] = []

            pets[pet_name]["medications"].append({
                "timestamp": timestamp,
                "medication": medication,
                "dose": dose,
                "notes": notes,
                "frequency": frequency,
                "interval_hours": interval_hours,
                "dosing_time": dosing_time,
                "next_due": next_due,
                "reminder_enabled": reminder_enabled
            })

            save_pets(pets)

            freq_display = format_frequency_display(frequency, interval_hours, dosing_time)
            note_part = f" | {notes}" if notes else ""
            print(color_text(f"✅ Added new medication: {medication} — {dose}{note_part}", Colors.GREEN))
            print(f"   👉 Frequency: {freq_display}")
            if next_due:
                print(f"   👉 Next due: {next_due}")
            if reminder_enabled:
                print(f"   👉 🔔 Reminder: ON")

        else:
            print(color_text("❌ Invalid option. Choose 0–4.", Colors.RED))

    print("="*60)
    input("Press Enter to return to main menu...")


def manage_feeding_schedule(pets):
    print("\n" + "="*60)
    print(color_text("🍽️  SET FEEDING SCHEDULE (NRC 2006 VET-GRADE)", Colors.MAGENTA + Colors.BOLD))
    print("="*60)

    if not pets:
        print(color_text("   🐾 No pets registered.", Colors.YELLOW))
        print("="*60)
        input("Press Enter to return...")
        return

    print("\nWhich pet do you want to set a feeding schedule for?")
    pet_names = list(pets.keys())
    for i, name in enumerate(pet_names, 1):
        print(f"   {i}. {name}")
    print("   0. Back")

    try:
        choice = int(input("Choose a pet (0 to cancel): ").strip())
        if choice == 0:
            return
        if choice < 1 or choice > len(pet_names):
            print(color_text("❌ Invalid choice.", Colors.RED))
            return
        pet_name = pet_names[choice - 1]
    except ValueError:
        print(color_text("❌ Invalid input.", Colors.RED))
        return

    pet = pets[pet_name]
    current_schedule = pet.get("feeding_schedule", [])
    current_reminders = pet.get("feeding_reminders", False)
    current_target_cal = pet.get("target_daily_calories")

    print(f"\n📝 Current settings for {pet_name}:")
    if current_schedule:
        print(f"   🕒 Scheduled times: {', '.join(current_schedule)}")
    else:
        print("   🕒 No scheduled times.")
    print(f"   🔔 Reminders: {'ON' if current_reminders else 'OFF'}")
    if current_target_cal:
        print(f"   🎯 Target calories: {current_target_cal} kcal/day")
    else:
        print("   🎯 Target calories: Not set")

    species = None
    while not species:
        species_input = input("\n🐾 What is the species of this pet? (dog/cat): ").strip().lower()
        if species_input in ["dog", "cat"]:
            species = species_input
        else:
            print(color_text("❌ Please enter 'dog' or 'cat'.", Colors.RED))

    if pet["weight"] is None:
        while True:
            try:
                weight_input = input("⚖️  Enter the pet's current weight in kg: ").strip()
                weight_kg = float(weight_input)
                if weight_kg <= 0:
                    print(color_text("❌ Weight must be positive.", Colors.RED))
                    continue
                pet["weight"] = weight_kg
                break
            except ValueError:
                print(color_text("❌ Invalid weight. Enter a number (e.g., 15.5).", Colors.RED))

    weight_kg = pet["weight"]

    activity_levels = {
        "1": "sedentary",
        "2": "normal",
        "3": "active",
        "4": "very_active"
    }
    print("\n🏃‍♂️  Select activity level:")
    print("   1. Sedentary (indoor, little movement)")
    print("   2. Normal (daily walks/play)")
    print("   3. Active (running, hiking, working)")
    print("   4. Very Active (high energy, sports, herding, etc.)")

    while True:
        act_choice = input("Choose 1-4: ").strip()
        if act_choice in activity_levels:
            activity_level = activity_levels[act_choice]
            break
        else:
            print(color_text("❌ Invalid choice. Choose 1–4.", Colors.RED))

    target_cal = calculate_daily_calories(weight_kg, species, activity_level)
    if target_cal is None:
        print(color_text("❌ Could not calculate calories. Please ensure weight and species are valid.", Colors.RED))
        return

    print(f"\n📊 Based on NRC 2006, ASPCA & Waltham guidelines:")
    print(f"   🐾 {species.capitalize()} ({weight_kg} kg) — {activity_level.title()} activity")
    print(f"   🎯 Recommended daily calories: {target_cal} kcal")

    while True:
        try:
            meal_count = int(input("\n🍽️  How many meals per day? (1–6): ").strip())
            if 1 <= meal_count <= 6:
                break
            else:
                print(color_text("❌ Please enter a number between 1 and 6.", Colors.RED))
        except ValueError:
            print(color_text("❌ Invalid input.", Colors.RED))

    schedule = []
    print(f"\n⏰ Set {meal_count} feeding times (24h format, HH:MM). Times will be evenly spaced.")

    for i in range(meal_count):
        hours_between = 24 / meal_count
        hour = int(i * hours_between)
        time_str = f"{hour:02d}:00"
        while True:
            time_input = input(f"   Meal {i+1} — Enter time (HH:MM) [default: {time_str}]: ").strip()
            if not time_input:
                time_input = time_str
            if len(time_input) == 5 and time_input[2] == ":":
                try:
                    h, m = map(int, time_input.split(":"))
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        time_formatted = f"{h:02d}:{m:02d}"
                        if time_formatted not in schedule:
                            schedule.append(time_formatted)
                            break
                        else:
                            print(color_text("   ⚠️  This time is already scheduled. Choose a different one.", Colors.YELLOW))
                    else:
                        raise ValueError
                except ValueError:
                    print(color_text("   ❌ Invalid time. Use HH:MM (e.g., 08:30).", Colors.RED))
            else:
                print(color_text("   ❌ Invalid format. Use HH:MM (e.g., 08:30).", Colors.RED))

    schedule.sort()

    while True:
        remind_choice = input("\n🔔 Enable feeding reminders? (y/N): ").strip().lower()
        if remind_choice in ['y', 'yes']:
            reminders = True
            break
        elif remind_choice in ['n', 'no', '']:
            reminders = False
            break
        else:
            print(color_text("❌ Please answer 'y' or 'n'.", Colors.RED))

    print("\n" + "="*60)
    print(color_text("✅ CONFIRMATION", Colors.GREEN))
    print("="*60)
    print(f"   Pet: {pet_name}")
    print(f"   Species: {species.capitalize()}")
    print(f"   Weight: {weight_kg} kg")
    print(f"   Activity: {activity_level.title()}")
    print(f"   Meals: {meal_count} per day")
    print(f"   Times: {', '.join(schedule)}")
    print(f"   Reminders: {'ON' if reminders else 'OFF'}")
    print(f"   Target Calories: {target_cal} kcal/day")

    confirm = input("\nSave these settings? (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        pet["feeding_schedule"] = schedule
        pet["feeding_reminders"] = reminders
        pet["target_daily_calories"] = target_cal
        save_pets(pets)
        print(color_text("✅ Feeding schedule, reminders, and target calories saved!", Colors.GREEN))
    else:
        print(color_text("❌ Settings not saved.", Colors.YELLOW))

    print("="*60)
    input("Press Enter to return to Settings...")


def change_weight_unit():
    print("\n" + "="*60)
    print(color_text("⚖️  CHANGE WEIGHT UNIT", Colors.BLUE + Colors.BOLD))
    print("="*60)

    prefs = load_user_prefs()
    current_unit = prefs.get("unit", "kg")
    print(f"Current unit: {current_unit.upper()}")

    print("\nChoose new unit:")
    print("   1. Kilograms (kg) — Recommended for most pets")
    print("   2. Pounds (lb) — Common in the US")
    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        new_unit = "kg"
    elif choice == "2":
        new_unit = "lb"
    else:
        print(color_text("❌ Invalid choice. No changes made.", Colors.RED))
        print("="*60)
        input("Press Enter to return...")
        return

    if new_unit == current_unit:
        print(color_text("ℹ️  Unit unchanged.", Colors.CYAN))
        print("="*60)
        input("Press Enter to return...")
        return

    pets = load_pets()
    converted_count = 0

    for pet_name, pet in pets.items():
        if pet["weight"] is not None:
            if current_unit == "kg" and new_unit == "lb":
                pet["weight"] = round(pet["weight"] * 2.20462, 2)
            elif current_unit == "lb" and new_unit == "kg":
                pet["weight"] = round(pet["weight"] / 2.20462, 2)
            converted_count += 1

        if "weights" in pet:
            for entry in pet["weights"]:
                if current_unit == "kg" and new_unit == "lb":
                    entry["weight"] = round(entry["weight"] * 2.20462, 2)
                elif current_unit == "lb" and new_unit == "kg":
                    entry["weight"] = round(entry["weight"] / 2.20462, 2)
                converted_count += 1

    save_pets(pets)
    prefs["unit"] = new_unit
    save_user_prefs(prefs)

    unit_name = "kilograms (kg)" if new_unit == "kg" else "pounds (lb)"
    print(color_text(f"✅ Successfully switched to {unit_name}!", Colors.GREEN))
    print(f"   💡 {converted_count} weight entries converted automatically.")
    print("="*60)
    input("Press Enter to return to main menu...")


def delete_all_data():
    print("\n" + "="*60)
    print(color_text("🗑️  DELETE ALL DATA", Colors.RED + Colors.BOLD))
    print("="*60)

    print(color_text("⚠️  THIS ACTION IS IRREVERSIBLE!", Colors.RED))
    print("All pet records, feedings, weights, medications, and logs will be permanently erased.")
    print("The file 'data/pets.json' will remain but will be empty.")

    confirm1 = input("\nAre you absolutely sure? Type 'DELETE ALL DATA' to confirm: ").strip()

    if confirm1 != "DELETE ALL DATA":
        print(color_text("❌ Operation cancelled.", Colors.YELLOW))
        print("="*60)
        input("Press Enter to return...")
        return

    confirm2 = input("Type 'I UNDERSTAND' to confirm final deletion: ").strip()

    if confirm2 != "I UNDERSTAND":
        print(color_text("❌ Operation cancelled.", Colors.YELLOW))
        print("="*60)
        input("Press Enter to return...")
        return

    save_pets({})
    print(color_text("✅ ALL PET DATA HAS BEEN ERASED. File 'data/pets.json' preserved as empty.", Colors.GREEN))
    print("You can now start fresh with a clean slate.")
    print("="*60)
    input("Press Enter to return to main menu...")


def reset_user_prefs():
    print("\n" + "="*60)
    print(color_text("🔧 RESET USER PREFERENCES", Colors.CYAN + Colors.BOLD))
    print("="*60)

    print("This will reset your weight unit to kilograms (kg) and clear any custom preferences.")
    print("Your pet data (names, weights, meds, etc.) will remain untouched.")

    confirm = input("\nAre you sure? (y/N): ").strip().lower()
    if confirm != "y":
        print(color_text("❌ Operation cancelled.", Colors.YELLOW))
        print("="*60)
        input("Press Enter to return...")
        return

    if os.path.exists(USER_PREFS_FILE):
        os.remove(USER_PREFS_FILE)
        print(color_text(f"🗑️  Deleted: {USER_PREFS_FILE}", Colors.CYAN))
    else:
        print(color_text(f"ℹ️  {USER_PREFS_FILE} not found — already reset.", Colors.YELLOW))

    print(color_text("✅ User preferences reset to defaults (unit: kg).", Colors.GREEN))
    print("Your pet data is safe and unchanged.")
    print("="*60)
    input("Press Enter to return to main menu...")


def calculate_daily_calories(weight_kg, species, activity_level):
    if weight_kg <= 0:
        return None

    rer = 70 * (weight_kg ** 0.75)

    if species.lower() == "dog":
        activity_multipliers = {
            "sedentary": 1.2,
            "normal": 1.6,
            "active": 2.0,
            "very_active": 3.0
        }
        multiplier = activity_multipliers.get(activity_level.lower(), 1.6)
    elif species.lower() == "cat":
        multiplier = 1.2
        if activity_level.lower() in ["active", "very_active"]:
            multiplier = 1.5
    else:
        return None

    daily_calories = rer * multiplier
    return round(daily_calories)


def export_logs_to_csv(pets, filepath="logs_export.csv"):
    """Export all logs to a CSV file."""
    import csv

    rows = []
    headers = ["Pet Name", "Log Type", "Details", "Timestamp", "Additional Info"]

    for pet_name, pet in pets.items():
        if "feedings" in pet:
            for feed in pet["feedings"]:
                rows.append([
                    pet_name,
                    "Feeding",
                    f"{feed['grams']}g ({feed['calories']} kcal)",
                    feed["timestamp"],
                    ""
                ])

    for pet_name, pet in pets.items():
        if "medications" in pet:
            for med in pet["medications"]:
                info = f"{med['medication']} — {med['dose']}"
                note = med.get("notes", "")
                rows.append([
                    pet_name,
                    "Medication",
                    info,
                    med["timestamp"],
                    note
                ])

    for pet_name, pet in pets.items():
        if "weights" in pet:
            for weight_entry in pet["weights"]:
                rows.append([
                    pet_name,
                    "Weight",
                    f"{weight_entry['weight']} kg",
                    weight_entry["date"],
                    ""
                ])

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(Colors.GREEN + f"✅ Logs exported successfully to: {filepath}" + Colors.RESET)
    except Exception as e:
        print(Colors.RED + f"❌ Failed to export CSV: {e}" + Colors.RESET)


def export_logs_to_json(pets, filepath="logs_export.json"):
    """Export all logs to a structured JSON file."""
    logs = {
        "feedings": [],
        "medications": [],
        "weights": []
    }

    for pet_name, pet in pets.items():
        if "feedings" in pet:
            for feed in pet["feedings"]:
                logs["feedings"].append({
                    "pet": pet_name,
                    "grams": feed["grams"],
                    "calories": feed["calories"],
                    "timestamp": feed["timestamp"]
                })

    for pet_name, pet in pets.items():
        if "medications" in pet:
            for med in pet["medications"]:
                logs["medications"].append({
                    "pet": pet_name,
                    "medication": med["medication"],
                    "dose": med["dose"],
                    "notes": med.get("notes", ""),
                    "frequency": med.get("frequency", ""),
                    "interval_hours": med.get("interval_hours", None),
                    "dosing_time": med.get("dosing_time", ""),
                    "next_due": med.get("next_due", ""),
                    "timestamp": med["timestamp"],
                    "reminder_enabled": med.get("reminder_enabled", False)
                })

    for pet_name, pet in pets.items():
        if "weights" in pet:
            for weight_entry in pet["weights"]:
                logs["weights"].append({
                    "pet": pet_name,
                    "weight": weight_entry["weight"],
                    "date": weight_entry["date"]
                })

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
        print(Colors.GREEN + f"✅ Full logs exported successfully to: {filepath}" + Colors.RESET)
    except Exception as e:
        print(Colors.RED + f"❌ Failed to export JSON: {e}" + Colors.RESET)