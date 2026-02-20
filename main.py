# main.py

from utils.logging_utils import (
    print_daily_summary,
    log_feeding_entry,
    log_medication_entry,
    log_weight_entry,
    toggle_reminder,
    snooze_reminder,
    set_quiet_hours,
    is_valid_time,
    start_feeding_scheduler,
    plot_weight_graph,
    plot_weekly_weight_trend
)
from utils.colors import Colors
import json
import os
from datetime import datetime

# --- DATA FILE ---
PETS_FILE = "data/pets.json"

# --- INITIALIZE PETS ---
def load_pets() -> dict:
    """Load pets from JSON file. Return empty dict if file doesn't exist."""
    if not os.path.exists(PETS_FILE):
        return {}
    try:
        with open(PETS_FILE, 'r', encoding='utf-8') as f:
            pets = json.load(f)
            # SAFETY MIGRATION: Ensure all pets have required fields
            for pet_id, pet_data in pets.items():
                # Add missing keys with defaults
                pet_data.setdefault("name", pet_id)
                pet_data.setdefault("species", "unknown")
                pet_data.setdefault("breed", "unknown")
                pet_data.setdefault("calorie_target", 100.0)
                pet_data.setdefault("feeding_reminder_enabled", False)
                pet_data.setdefault("medication_reminder_enabled", False)
                pet_data.setdefault("feeding_schedule", [])
                pet_data.setdefault("medication_times", [])
                pet_data.setdefault("snooze_until", None)
                pet_data.setdefault("quiet_hours", None)
            return pets
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        print(Colors.RED + "⚠️ Corrupted or unreadable pets file. Starting fresh." + Colors.RESET)
        return {}

def save_pets(pets: dict):
    """Save pets to JSON file."""
    try:
        os.makedirs(os.path.dirname(PETS_FILE), exist_ok=True)
        with open(PETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(pets, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(Colors.RED + f"❌ Failed to save pets: {e}" + Colors.RESET)

def delete_all_data():
    """Delete all pet and log data."""
    for file in [PETS_FILE, "data/logs.json"]:
        if os.path.exists(file):
            os.remove(file)
            print(Colors.RED + f"🗑️ Deleted: {file}" + Colors.RESET)
    print(Colors.RED + "🔥 ALL DATA HAS BEEN PERMANENTLY DELETED." + Colors.RESET)

# --- MENU: EDIT PET ---
def edit_pet(pets: dict):
    """Edit existing pet details."""
    if not pets:
        print(Colors.YELLOW + "📭 No pets to edit." + Colors.RESET)
        return

    print("\n" + "="*40)
    print(f"{Colors.CYAN}✏️ EDIT PET{Colors.RESET}")
    print("="*40)
    for i, name in enumerate(pets.keys(), 1):
        print(f"{i}. {name}")

    try:
        idx = int(input("Select pet to edit (number): ")) - 1
        pet_name = list(pets.keys())[idx]
        pet = pets[pet_name]

        print(f"\nEditing: {pet_name}")
        print(f"Current: {pet.get('species', 'unknown')} | {pet.get('breed', 'unknown')} | Target: {pet.get('calorie_target', 100)} kcal")

        new_species = input(f"New species (leave blank to keep '{pet.get('species', 'unknown')}'): ").strip()
        if new_species:
            pet['species'] = new_species

        new_breed = input(f"New breed (leave blank to keep '{pet.get('breed', 'unknown')}'): ").strip()
        if new_breed:
            pet['breed'] = new_breed

        cal_str = input(f"New calorie target (leave blank to keep {pet.get('calorie_target', 100)}): ").strip()
        if cal_str:
            pet['calorie_target'] = float(cal_str)

        save_pets(pets)
        print(Colors.GREEN + f"✅ Updated: {pet_name}" + Colors.RESET)

    except (ValueError, IndexError):
        print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

# --- MENU: LOG SOMETHING ---
def log_something(pets: dict):
    """Submenu for logging feeding, medication, or weight."""
    if not pets:
        print(Colors.YELLOW + "📭 No pets registered. Add a pet first." + Colors.RESET)
        return

    print("\n" + "="*40)
    print(f"{Colors.CYAN}📝 LOG SOMETHING{Colors.RESET}")
    print("="*40)
    print("1. Log Feeding")
    print("2. Log Medication")
    print("3. Log Weight")
    print("0. Back")

    choice = input("Choose: ").strip()

    if choice == "1":
        print("\nSelect pet:")
        for i, name in enumerate(pets.keys(), 1):
            print(f"{i}. {name}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            grams = float(input("Enter food amount (grams): "))
            calories = float(input("Enter calories (kcal): "))
            log_feeding_entry(pets, pet_name, grams, calories)
            print(Colors.GREEN + f"✅ Logged: {grams}g ({calories} kcal) for {pet_name}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "2":
        print("\nSelect pet:")
        for i, name in enumerate(pets.keys(), 1):
            print(f"{i}. {name}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            dose = input("Enter medication details (e.g., '5mg insulin'): ").strip()
            if not dose:
                print(Colors.YELLOW + "❌ Medication details required." + Colors.RESET)
                return
            log_medication_entry(pets, pet_name, dose)
            print(Colors.GREEN + f"✅ Logged medication: {dose} for {pet_name}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "3":
        print("\nSelect pet:")
        for i, name in enumerate(pets.keys(), 1):
            print(f"{i}. {name}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            weight = float(input("Enter current weight (kg): "))
            log_weight_entry(pets, pet_name, weight)
            print(Colors.GREEN + f"✅ Logged weight: {weight}kg for {pet_name}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "0":
        return
    else:
        print(Colors.RED + "❌ Invalid option." + Colors.RESET)

# --- MENU: REMINDERS ---
def manage_reminders(pets: dict):
    """Submenu for managing reminders, snooze, quiet hours."""
    if not pets:
        print(Colors.YELLOW + "📭 No pets registered." + Colors.RESET)
        return

    print("\n" + "="*40)
    print(f"{Colors.CYAN}🔔 REMINDERS{Colors.RESET}")
    print("="*40)
    print("1. Toggle Feeding Reminder (individual)")
    print("2. Toggle Medication Reminder (individual)")
    print("3. Toggle All Reminders ON/OFF")
    print("4. Snooze All Reminders (2 hrs)")
    print("5. Set Quiet Hours")
    print("0. Back")

    choice = input("Choose: ").strip()

    if choice == "1":
        print("\nSelect pet to toggle feeding reminder:")
        for i, name in enumerate(pets.keys(), 1):
            status = "ON" if pets[name].get("feeding_reminder_enabled", False) else "OFF"
            print(f"{i}. {name} — {status}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            toggle_reminder(pets, pet_name, "feeding")
            status = "ON" if pets[pet_name].get("feeding_reminder_enabled", False) else "OFF"
            save_pets(pets)
            print(Colors.GREEN + f"✅ Feeding reminder for {pet_name} is now {status}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

    elif choice == "2":
        print("\nSelect pet to toggle medication reminder:")
        for i, name in enumerate(pets.keys(), 1):
            status = "ON" if pets[name].get("medication_reminder_enabled", False) else "OFF"
            print(f"{i}. {name} — {status}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            toggle_reminder(pets, pet_name, "medication")
            status = "ON" if pets[pet_name].get("medication_reminder_enabled", False) else "OFF"
            save_pets(pets)
            print(Colors.GREEN + f"✅ Medication reminder for {pet_name} is now {status}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

    elif choice == "3":
        print("\nSelect pet to toggle ALL reminders:")
        for i, name in enumerate(pets.keys(), 1):
            feed_status = "ON" if pets[name].get("feeding_reminder_enabled", False) else "OFF"
            med_status = "ON" if pets[name].get("medication_reminder_enabled", False) else "OFF"
            print(f"{i}. {name} — Feeding: {feed_status} | Medication: {med_status}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            # Toggle both
            current_feed = pets[pet_name].get("feeding_reminder_enabled", False)
            current_med = pets[pet_name].get("medication_reminder_enabled", False)
            new_state = not (current_feed or current_med)  # If either is on, turn both off. Else, turn both on.
            pets[pet_name]["feeding_reminder_enabled"] = new_state
            pets[pet_name]["medication_reminder_enabled"] = new_state
            save_pets(pets)
            state_str = "ON" if new_state else "OFF"
            print(Colors.GREEN + f"✅ All reminders for {pet_name} set to {state_str}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

    elif choice == "4":
        print("\nSelect pet to snooze reminders:")
        for i, name in enumerate(pets.keys(), 1):
            print(f"{i}. {name}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            snooze_reminder(pets, pet_name, 2)
            save_pets(pets)
            print(Colors.GREEN + f"✅ Reminders snoozed for {pet_name} until 2 hours from now." + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

    elif choice == "5":
        print("\nSelect pet to set quiet hours:")
        for i, name in enumerate(pets.keys(), 1):
            print(f"{i}. {name}")
        try:
            idx = int(input("Enter number: ")) - 1
            pet_name = list(pets.keys())[idx]
            start = input("Enter quiet start time (HH:MM): ").strip()
            end = input("Enter quiet end time (HH:MM): ").strip()
            if not is_valid_time(start) or not is_valid_time(end):
                print(Colors.RED + "❌ Invalid time format. Use HH:MM (e.g., 22:00)." + Colors.RESET)
                return
            set_quiet_hours(pets, pet_name, start, end)
            save_pets(pets)
            print(Colors.GREEN + f"✅ Quiet hours set for {pet_name}: {start} - {end}" + Colors.RESET)
        except (ValueError, IndexError):
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

    elif choice == "0":
        return
    else:
        print(Colors.RED + "❌ Invalid option." + Colors.RESET)

# --- MENU: DAILY SUMMARY ---
def daily_summary(pets: dict):
    """Show daily summary for a single selected pet."""
    if not pets:
        print(Colors.YELLOW + "📭 No pets registered." + Colors.RESET)
        return

    print("\n" + "="*40)
    print(f"{Colors.CYAN}📊 DAILY SUMMARY{Colors.RESET}")
    print("="*40)
    print("Select a pet to view daily summary:")

    for i, name in enumerate(pets.keys(), 1):
        print(f"{i}. {name}")

    try:
        idx = int(input("Enter number: ")) - 1
        pet_name = list(pets.keys())[idx]
        print(f"\n{Colors.CYAN}📋 DAILY SUMMARY FOR {pet_name.upper()}{Colors.RESET}")
        print_daily_summary(pets, pet_name)  # Pass pet_name to show only one
    except (ValueError, IndexError):
        print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

# --- MAIN MENU ---
def main():
    pets = load_pets()  # ✅ This now auto-migrates old data!
    start_feeding_scheduler(pets)  # Start background reminder thread

    while True:
        print("\n" + "="*60)
        print(f"{Colors.CYAN}🐾 PET HEALTH TRACKER v3.1{Colors.RESET}")
        print("="*60)
        print("1. Add New Pet")
        print("2. Edit Pet")
        print("3. List All Pets")
        print("4. Log Something")
        print("5. Reminders")
        print("6. Daily Summary")
        print("7. Weekly Weight Trend")
        print("8. View All Logs (JSON)")
        print("9. Delete All Data")
        print("0. Exit")
        print("-"*60)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Enter pet name: ").strip()
            if not name:
                print(Colors.YELLOW + "❌ Name cannot be empty." + Colors.RESET)
                continue
            species = input("Enter species (dog/cat/etc): ").strip() or "unknown"
            breed = input("Enter breed (optional): ").strip() or "unknown"
            cal_str = input("Enter daily calorie target (kcal, default 100): ").strip()
            calorie_target = float(cal_str) if cal_str else 100.0

            pets[name] = {
                "name": name,
                "species": species,
                "breed": breed,
                "calorie_target": calorie_target,
                "feeding_reminder_enabled": False,
                "medication_reminder_enabled": False,
                "feeding_schedule": [],
                "medication_times": [],
                "snooze_until": None,
                "quiet_hours": None
            }
            save_pets(pets)
            print(Colors.GREEN + f"✅ Added pet: {name}" + Colors.RESET)

        elif choice == "2":
            edit_pet(pets)

        elif choice == "3":
            if not pets:
                print(Colors.YELLOW + "📭 No pets registered." + Colors.RESET)
            else:
                print(f"\n{Colors.CYAN}📋 LIST OF PETS{Colors.RESET}")
                for pet_id, info in pets.items():
                    pet_name = info.get("name", "Unnamed Pet")
                    species = info.get("species", "unknown")
                    breed = info.get("breed", "unknown")
                    cal_target = info.get("calorie_target", 100.0)
                    print(f"  {Colors.CYAN}{pet_name}{Colors.RESET} | {species} | {breed} | Target: {cal_target:.1f} kcal")

        elif choice == "4":
            log_something(pets)

        elif choice == "5":
            manage_reminders(pets)

        elif choice == "6":
            daily_summary(pets)

        elif choice == "7":
            if not pets:
                print(Colors.YELLOW + "📭 No pets registered." + Colors.RESET)
                continue
            print("\nSelect pet:")
            for i, name in enumerate(pets.keys(), 1):
                print(f"{i}. {name}")
            try:
                idx = int(input("Enter number: ")) - 1
                pet_name = list(pets.keys())[idx]
                plot_weekly_weight_trend(pets, pet_name)
            except (ValueError, IndexError):
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)

        elif choice == "8":
            logs = load_logs()  # Helper below
            print(f"\n{Colors.CYAN}📜 ALL LOGS (JSON){Colors.RESET}")
            print(json.dumps(logs, indent=2, ensure_ascii=False))

        elif choice == "9":
            confirm = input("⚠️  ARE YOU SURE? This will delete ALL pet and log data. Type 'YES' to confirm: ").strip().upper()
            if confirm == "YES":
                delete_all_data()
                pets = {}  # Reset in memory
            else:
                print(Colors.YELLOW + "❌ Deletion cancelled." + Colors.RESET)

        elif choice == "0":
            print(Colors.CYAN + "👋 Goodbye! Caring for pets is important." + Colors.RESET)
            break

        else:
            print(Colors.RED + "❌ Invalid option. Try again." + Colors.RESET)

# --- Helper to load logs (for menu option 8) ---
def load_logs() -> list:
    """Load logs from JSON file. Returns empty list if not found or corrupted."""
    LOGS_FILE = "data/logs.json"
    if not os.path.exists(LOGS_FILE):
        return []
    try:
        with open(LOGS_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            return logs if isinstance(logs, list) else []
    except Exception:
        return []

if __name__ == "__main__":
    main()