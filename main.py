import json
from typing import Dict
from pathlib import Path
# Import your custom utilities
from utils.logging_utils import (
    log_feeding_entry,
    log_medication_entry,
    log_weight_entry,
    print_daily_summary,
    plot_weight_graph,
    plot_weekly_weight_trend,
    log_action,
    calculate_recent_weight_change,
    start_feeding_scheduler,
    toggle_reminder,
    snooze_reminder,
    set_quiet_hours,
    Pet  # 👈 Import Pet type
)
from utils.calorie_calculator import calculate_calories
from utils.pet_editor import edit_pet
# CONFIGURATION
PETS_FILE = "pets.json"  # 👈 DEFINED HERE — FIXED THE ERROR!
# --- ANSI colors ---
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    END = "\033[0m"
def color_text(text, color):
    return f"{color}{text}{Colors.END}"
# --- Load pets with automatic migration ---
try:
    with open(PETS_FILE, "r", encoding="utf-8") as f:
        pets: Dict[str, Pet] = json.load(f)
        if not isinstance(pets, dict):
            pets = {}
except FileNotFoundError:
    pets = {}
# --- MIGRATION: Clean up inconsistent pet data ---
def migrate_pet_data():
    """Migrate old pet structures to consistent schema."""
    for pet_id in list(pets.keys()):
        pet = pets[pet_id]
        # Remove redundant feeding_schedule if present
        if "feeding_schedule" in pet:
            del pet["feeding_schedule"]
        # Migrate reminder_settings → top-level fields
        if "reminder_settings" in pet:
            settings = pet.pop("reminder_settings")
            pet["reminder_enabled"] = settings.get("enabled", False)
            pet["quiet_hours"] = settings.get("quiet_hours", {"start": None, "end": None})
            pet["snooze_until"] = settings.get("snoozed_until", None)
        # Ensure required fields exist
        pet.setdefault("reminder_enabled", False)
        pet.setdefault("quiet_hours", {"start": None, "end": None})
        pet.setdefault("snooze_until", None)
        pet.setdefault("feeding_times", [])
migrate_pet_data()
# --- Helper Functions ---
def save_pets():
    with open(PETS_FILE, "w", encoding="utf-8") as f:
        json.dump(pets, f, indent=2, ensure_ascii=False)
def confirm_action(message):
    while True:
        response = input(f"{message} (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            print("Action cancelled.\n")
            return False
        else:
            print("Please type 'yes' or 'no'.")
def find_pet_by_name():
    name = input("Enter pet name to search: ").strip()
    for pet_id, pet in pets.items():
        if pet["name"].lower() == name.lower():
            print(f"✅ Found: {pet['name']}")
            # Auto warnings
            total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
            target = pet.get("calorie_target", 0)
            if total_cal < target:
                print(color_text(f"⚠️ {pet['name']} calories below target today: {total_cal}/{target}", Colors.RED))
            weekly_change = calculate_recent_weight_change(pet)
            if abs(weekly_change) >= 5:
                print(color_text(f"⚠️ Rapid weight change in last 7 days: {weekly_change:+.1f}%", Colors.RED))
            # Reminder status
            reminder_status = "🟢 On" if pet.get("reminder_enabled", False) else "🔴 Off"
            print(f"Reminder status: {reminder_status}")
            return pet, pet_id
    print(color_text("⚠️ Pet not found.", Colors.RED))
    return None, None
# --- Mini-sparkline generator ---
def mini_sparkline(pet, width=20):
    history = pet.get("weight_history", [])
    if len(history) < 2:
        return ""
    weights = [h["weight"] for h in history[-width:]]
    spark = ""
    prev = None
    for w in weights:
        if prev is None:
            color = Colors.YELLOW
        elif w > prev:
            color = Colors.GREEN
        elif w < prev:
            color = Colors.RED
        else:
            color = Colors.YELLOW
        spark += color_text("▇", color)
        prev = w
    return spark
# --- Main loop ---
def main():
    # Start background feeding scheduler for all pets
    for pet in pets.values():
        if pet.get("reminder_enabled", False):
            start_feeding_scheduler(pet, pets)  # ✅ Pass the global pets dict
    while True:
        print("""
╔═══════════════════════════════════════════╗
 🌸🐾   P a w C a r e   T r a c k e r 🐾🌸
╚═══════════════════════════════════════════╝
1 Add Pet
2 Edit Pet
3 Search Pet by Name
4 Log Feeding
5 Log Medication
6 Log Weight
7 Daily Summary
8 Weight Graph
9 Weekly Weight Trend
10 Reminders
11 Set Feeding Schedule
X Delete All Data
0 Exit
""")
        choice = input("Choose an option: ").strip()
        # --------------------------
        # Add Pet
        # --------------------------
        if choice == "1":
            name = input("Pet name: ").strip()
            weight = float(input("Weight (kg): "))
            cal_target = int(input("Daily calorie target: "))
            cal_density = int(input("Food calorie density per 100g: "))
            pet_id = str(max([int(k) for k in pets.keys()] + [0]) + 1)
            pets[pet_id] = {
                "name": name,
                "weight": weight,
                "calorie_target": cal_target,
                "calorie_density": cal_density,
                "feedings": [],
                "medications": [],
                "weight_history": [],
                "feeding_times": ["09:00", "15:00", "21:00"],
                "reminder_enabled": True,
                "snooze_until": None,
                "quiet_hours": {"start": None, "end": None}
            }
            save_pets()
            log_action(f"🐾 Added new pet: {name}")
            print(color_text(f"✅ {name} added!\n", Colors.GREEN))
            if pets[pet_id]["reminder_enabled"]:
                start_feeding_scheduler(pets[pet_id], pets)  # ✅ Pass pets dict
        # --------------------------
        # Edit Pet
        # --------------------------
        elif choice == "2":
            pet, pet_id = find_pet_by_name()
            if pet and confirm_action(f"✏️ Are you sure you want to edit {pet['name']}?"):
                edit_pet(pet)
                save_pets()
                log_action(f"✏️ Edited pet: {pet['name']}")
                print(color_text(f"✅ {pet['name']} updated.\n", Colors.GREEN))
        # --------------------------
        # Search Pet
        # --------------------------
        elif choice == "3":
            pet, pet_id = find_pet_by_name()
            if pet:
                print()
        # --------------------------
        # Log Feeding
        # --------------------------
        elif choice == "4":
            pet, pet_id = find_pet_by_name()
            if pet:
                grams = float(input("Grams fed: "))
                log_feeding_entry(pet, grams)
                save_pets()
                total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
                if total_cal < pet.get("calorie_target", 0):
                    print(color_text(f"⚠️ Feeding below daily calorie target! ({total_cal}/{pet['calorie_target']})", Colors.RED))
                print(color_text(f"✅ Feeding logged for {pet['name']}.\n", Colors.GREEN))
        # --------------------------
        # Log Medication
        # --------------------------
        elif choice == "5":
            pet, pet_id = find_pet_by_name()
            if pet:
                med_name = input("Medication name: ").strip()
                dose = input("Dose: ").strip()
                if confirm_action(f"💊 Log {dose} of {med_name} for {pet['name']}?"):
                    log_medication_entry(pet, med_name, dose)
                    save_pets()
                    print(color_text(f"✅ Medication logged for {pet['name']}.\n", Colors.GREEN))
        # --------------------------
        # Log Weight
        # --------------------------
        elif choice == "6":
            pet, pet_id = find_pet_by_name()
            if pet:
                weight = float(input("Enter new weight (kg): "))
                if confirm_action(f"⚖️ Log new weight {weight}kg for {pet['name']}?"):
                    log_weight_entry(pet, weight)
                    save_pets()
                    print(color_text(f"✅ Weight logged for {pet['name']}.\n", Colors.GREEN))
                    weekly_change = calculate_recent_weight_change(pet)
                    if abs(weekly_change) >= 5:
                        print(color_text(f"⚠️ Rapid weight change in last 7 days: {weekly_change:+.1f}%\n", Colors.RED))
        # --------------------------
        # Daily Summary
        # --------------------------
        elif choice == "7":
            pet, pet_id = find_pet_by_name()
            if pet:
                print_daily_summary(pet)
                spark = mini_sparkline(pet)
                if spark:
                    print(f"📈 Weight trend: {spark}\n")
        # --------------------------
        # Weight Graph
        # --------------------------
        elif choice == "8":
            pet, pet_id = find_pet_by_name()
            if pet:
                plot_weight_graph(pet)
        # --------------------------
        # Weekly Weight Trend
        # --------------------------
        elif choice == "9":
            pet, pet_id = find_pet_by_name()
            if pet:
                plot_weekly_weight_trend(pet)
        # --------------------------
        # Reminders Menu
        # --------------------------
        elif choice == "10":
            pet, pet_id = find_pet_by_name()
            if pet:
                while True:
                    print(f"""
--- Reminders for {pet['name']} ---
1️⃣ Toggle Reminder On/Off
2️⃣ Snooze Reminder (minutes)
3️⃣ Set Quiet Hours
4️⃣ Back to Main Menu
Current status: {"🟢 On" if pet.get("reminder_enabled") else "🔴 Off"}
""")
                    r_choice = input("Choose an option: ").strip()
                    if r_choice == "1":
                        toggle_reminder(pet)
                        save_pets()
                    elif r_choice == "2":
                        minutes = int(input("Snooze for how many minutes? "))
                        snooze_reminder(pet, minutes)
                        save_pets()
                    elif r_choice == "3":
                        start = input("Quiet hours start (HH:MM or empty): ").strip() or None
                        end = input("Quiet hours end (HH:MM or empty): ").strip() or None
                        set_quiet_hours(pet, start, end)
                        save_pets()
                    elif r_choice == "4":
                        break
                    else:
                        print(color_text("⚠️ Invalid choice. Try again.\n", Colors.RED))
        # --------------------------
        # Set Feeding Schedule
        # --------------------------
        elif choice == "11":
            pet, pet_id = find_pet_by_name()
            if pet:
                print(f"\nCurrent feeding times: {pet.get('feeding_times', [])}")
                times_input = input("Enter feeding times separated by commas (HH:MM): ").strip()
                if times_input:
                    pet["feeding_times"] = [t.strip() for t in times_input.split(",")]
                enable_reminder = input("Enable reminders? (yes/no): ").strip().lower()
                pet["reminder_enabled"] = enable_reminder in ["yes", "y"]
                save_pets()
                print(color_text(f"✅ Feeding schedule updated for {pet['name']}\n", Colors.GREEN))
                if pet["reminder_enabled"]:
                    start_feeding_scheduler(pet, pets)  # ✅ Pass pets dict
        # --------------------------
        # Delete All Data
        # --------------------------
        elif choice.upper() == "X":
            if confirm_action("⚠️ Are you sure you want to DELETE ALL DATA? This cannot be undone."):
                if confirm_action("❗ Please confirm AGAIN to permanently delete all data."):
                    pets.clear()
                    save_pets()
                    log_action("🗑️ All data deleted")
                    print(color_text("✅ All data deleted!\n", Colors.RED))
        # --------------------------
        # Exit
        # --------------------------
        elif choice.upper() == "0":
            print("Goodbye! 🌸")
            break
        else:
            print(color_text("⚠️ Invalid choice. Try again.\n", Colors.RED))
if __name__ == "__main__":
    main()