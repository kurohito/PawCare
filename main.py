# main.py

from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication
from utils.logging_utils import log_action
from utils.pet_editor import edit_pet
import json

PET_FILE = "pets.json"

def load_pets():
    try:
        with open(PET_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_pets(pets):
    with open(PET_FILE, "w") as f:
        json.dump(pets, f, indent=4)

def add_pet():
    pets = load_pets()
    name = input("Pet name: ").strip()
    while True:
        try:
            weight = float(input("Weight in kg: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    while True:
        try:
            calorie_target = float(input("Daily calorie target: "))
            break
        except ValueError:
            print("Please enter a valid number.")

    pets.append({
        "name": name,
        "weight": weight,
        "calorie_target": calorie_target,
        "feedings": [],
        "medications": [],
        "weight_history": []
    })
    save_pets(pets)
    log_action(f"Added new pet: {name}")
    print(f"{name} added successfully!\n")

def log_feeding(pet_name):
    pets = load_pets()
    pet = next((p for p in pets if p["name"].lower() == pet_name.lower()), None)
    if not pet:
        print(f"No pet found with the name '{pet_name}'.")
        return

    while True:
        try:
            grams = float(input("Grams fed: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    calories = calculate_calories(grams)
    pet["feedings"].append({
        "grams": grams,
        "calories": calories
    })
    save_pets(pets)
    log_action(f"Logged feeding for {pet['name']}: {grams}g ({calories} cal)")
    print(f"Feeding logged: {grams}g ({calories} cal)\n")

def daily_summary(pet_name):
    pets = load_pets()
    pet = next((p for p in pets if p["name"].lower() == pet_name.lower()), None)
    if not pet:
        print(f"No pet found with the name '{pet_name}'.")
        return

    total_calories = sum(f["calories"] for f in pet["feedings"])
    print(f"\nDaily Summary for {pet['name']}:")
    print(f"Weight: {pet['weight']} kg")
    print(f"Total Calories: {total_calories}/{pet['calorie_target']}")
    print(f"Feedings logged: {len(pet['feedings'])}")
    print(f"Medications logged: {len(pet['medications'])}\n")

def delete_all_data():
    """Safely delete all pet data with double confirmation."""
    confirm1 = input("Are you sure you want to delete ALL pet data? (y/n): ").strip().lower()
    if confirm1 != "y":
        print("Delete cancelled.\n")
        return

    confirm2 = input("This cannot be undone! Type DELETE to confirm: ").strip()
    if confirm2 != "DELETE":
        print("Delete cancelled.\n")
        return

    with open(PET_FILE, "w") as f:
        f.write("[]")  # Reset JSON to empty list

    log_action("All pet data deleted")
    print("All pet data deleted successfully! 💛\n")

def main_menu():
    while True:
        print("\n🌸🐾 PawCare Main Menu 🌸🐾")
        print("1. Add Pet")
        print("2. Edit Pet")
        print("3. Log Feeding")
        print("4. Log Medication")
        print("5. Daily Summary")
        print("6. Delete All Pet Data")
        print("7. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_pet()
        elif choice == "2":
            pet_name = input("Enter the name of the pet to edit: ").strip()
            edit_pet(pet_name)
        elif choice == "3":
            pet_name = input("Enter the name of the pet: ").strip()
            log_feeding(pet_name)
        elif choice == "4":
            pet_name = input("Enter the name of the pet: ").strip()
            log_medication(pet_name)
        elif choice == "5":
            pet_name = input("Enter the name of the pet: ").strip()
            daily_summary(pet_name)
        elif choice == "6":
            delete_all_data()
        elif choice == "7":
            print("Goodbye! 🌸🐾")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()