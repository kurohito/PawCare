# main.py

import json
from utils.logging_utils import (
    log_feeding_entry,
    log_medication_entry,
    log_weight_entry,
    print_daily_summary,
    plot_weight_graph,
    log_action
)
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication
from utils.pet_editor import edit_pet

PETS_FILE = "pets.json"

# --- Load pets ---
try:
    with open(PETS_FILE, "r") as f:
        pets = json.load(f)
        if isinstance(pets, list):
            # Convert old list format to dict with string keys
            pets = {str(i+1): pet for i, pet in enumerate(pets)}
except FileNotFoundError:
    pets = {}

# --- Helper functions ---

def save_pets():
    with open(PETS_FILE, "w") as f:
        json.dump(pets, f, indent=2)

def confirm_action(message):
    """Ask user to confirm critical action."""
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
    for pet in pets.values():
        if pet["name"].lower() == name.lower():
            print(f"✅ Found: {pet['name']}")
            return pet
    print("⚠️ Pet not found.")
    return None

# --- Main loop ---
def main():
    while True:
        print("""
🌸 PawCare Tracker 🌸
1. Add Pet
2. Edit Pet
3. Search Pet by Name
4. Log Feeding
5. Log Medication
6. Log Weight
7. Daily Summary
8. Weight Graph
9. Delete All Data
0. Exit
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Pet name: ").strip()
            weight = float(input("Weight (kg): "))
            cal_target = int(input("Daily calorie target: "))
            cal_density = int(input("Food calorie density per 100g: "))

            # Generate next pet ID safely
            pet_id = str(max([int(k) for k in pets.keys()] + [0]) + 1)

            pets[pet_id] = {
                "name": name,
                "weight": weight,
                "calorie_target": cal_target,
                "calorie_density": cal_density,
                "feedings": [],
                "medications": [],
                "weight_history": []
            }
            save_pets()
            log_action(f"🐾 Added new pet: {name}")
            print(f"✅ {name} added!\n")

        elif choice == "2":
            pet = find_pet_by_name()
            if pet and confirm_action(f"✏️ Are you sure you want to edit {pet['name']}?"):
                edit_pet(pet)
                save_pets()
                log_action(f"✏️ Edited pet: {pet['name']}")
                print(f"✅ {pet['name']} updated.\n")

        elif choice == "3":
            find_pet_by_name()
            print()

        elif choice == "4":
            pet = find_pet_by_name()
            if pet:
                grams = float(input("Grams fed: "))
                log_feeding_entry(pet, grams)
                save_pets()
                print(f"✅ Feeding logged for {pet['name']}.\n")

        elif choice == "5":
            pet = find_pet_by_name()
            if pet:
                med_name = input("Medication name: ").strip()
                dose = input("Dose: ").strip()
                if confirm_action(f"💊 Log {dose} of {med_name} for {pet['name']}?"):
                    log_medication_entry(pet, med_name, dose)
                    save_pets()
                    print(f"✅ Medication logged for {pet['name']}.\n")

        elif choice == "6":
            pet = find_pet_by_name()
            if pet:
                weight = float(input("Enter new weight (kg): "))
                if confirm_action(f"⚖️ Log new weight {weight}kg for {pet['name']}?"):
                    log_weight_entry(pet, weight)
                    save_pets()
                    print(f"✅ Weight logged for {pet['name']}.\n")

        elif choice == "7":
            pet = find_pet_by_name()
            if pet:
                print_daily_summary(pet)

        elif choice == "8":
            pet = find_pet_by_name()
            if pet:
                plot_weight_graph(pet)

        elif choice == "9":
            if confirm_action("⚠️ Are you sure you want to DELETE ALL DATA? This cannot be undone."):
                if confirm_action("❗ Please confirm AGAIN to permanently delete all data."):
                    pets.clear()
                    save_pets()
                    log_action("🗑️ All data deleted")
                    print("✅ All data deleted!\n")

        elif choice == "0":
            print("Goodbye! 🌸")
            break

        else:
            print("⚠️ Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()