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
        "weight_history": [{"weight": weight}]
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

    # Optional weight update during feeding
    update_weight = input("Update weight? (y/n): ").strip().lower()
    if update_weight == "y":
        while True:
            try:
                new_weight = float(input("New weight in kg: "))
                pet["weight"] = new_weight
                pet["weight_history"].append({"weight": new_weight})
                log_action(f"Updated weight for {pet_name}: {new_weight} kg")
                print(f"Weight updated to {new_weight} kg.\n")
                break
            except ValueError:
                print("Please enter a valid number.")

    save_pets(pets)
    log_action(f"Logged feeding for {pet['name']}: {grams}g ({calories} cal)")
    print(f"Feeding logged: {grams}g ({calories} cal)\n")

def log_weight():
    """Standalone weight logging."""
    pets = load_pets()
    pet_name = input("Enter the name of the pet: ").strip()
    pet = next((p for p in pets if p["name"].lower() == pet_name.lower()), None)
    if not pet:
        print(f"No pet found with the name '{pet_name}'.")
        return

    while True:
        try:
            new_weight = float(input(f"Enter new weight for {pet['name']} in kg: "))
            break
        except ValueError:
            print("Please enter a valid number.")

    pet["weight"] = new_weight
    pet["weight_history"].append({"weight": new_weight})
    save_pets(pets)
    log_action(f"Updated weight for {pet['name']}: {new_weight} kg")
    print(f"Weight for {pet['name']} updated to {new_weight} kg.\n")

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

def search_pet():
    """Search for pets by name and allow immediate actions."""
    pets = load_pets()
    query = input("Enter the pet name to search: ").strip().lower()
    matches = [p for p in pets if query in p["name"].lower()]

    if not matches:
        print(f"No pets found matching '{query}'.\n")
        return

    print(f"\nFound {len(matches)} pet(s):")
    for i, pet in enumerate(matches, 1):
        print(f"{i}. Name: {pet['name']}, Weight: {pet['weight']} kg, Daily Calories: {pet['calorie_target']}")

    while True:
        try:
            selection = int(input("\nSelect a pet by number to manage it, or 0 to cancel: "))
            if selection == 0:
                print("Returning to main menu.\n")
                return
            if 1 <= selection <= len(matches):
                chosen_pet = matches[selection - 1]
                break
            else:
                print("Invalid number. Try again.")
        except ValueError:
            print("Please enter a valid number.")

    # Sub-menu for the selected pet
    while True:
        print(f"\n🌸 Managing {chosen_pet['name']} 🌸")
        print("1. Edit Pet")
        print("2. Log Feeding")
        print("3. Log Medication")
        print("4. Daily Summary")
        print("5. Return to Main Menu")

        action = input("Choose an action: ").strip()
        if action == "1":
            edit_pet(chosen_pet["name"])
        elif action == "2":
            log_feeding(chosen_pet["name"])
        elif action == "3":
            log_medication(chosen_pet["name"])
        elif action == "4":
            daily_summary(chosen_pet["name"])
        elif action == "5":
            print("Returning to main menu.\n")
            return
        else:
            print("Invalid choice. Please try again.")

def main_menu():
    while True:
        print("\n🌸🐾 PawCare Main Menu 🌸🐾")
        print("1. Add Pet")
        print("2. Edit Pet")
        print("3. Search Pet by Name")
        print("4. Log Weight")            # NEW
        print("5. Log Feeding")
        print("6. Log Medication")
        print("7. Daily Summary")
        print("8. Delete All Pet Data")
        print("9. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_pet()
        elif choice == "2":
            pet_name = input("Enter the name of the pet to edit: ").strip()
            edit_pet(pet_name)
        elif choice == "3":
            search_pet()
        elif choice == "4":
            log_weight()
        elif choice == "5":
            pet_name = input("Enter the name of the pet: ").strip()
            log_feeding(pet_name)
        elif choice == "6":
            pet_name = input("Enter the name of the pet: ").strip()
            log_medication(pet_name)
        elif choice == "7":
            pet_name = input("Enter the name of the pet: ").strip()
            daily_summary(pet_name)
        elif choice == "8":
            delete_all_data()
        elif choice == "9":
            print("Goodbye! 🌸🐾")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()