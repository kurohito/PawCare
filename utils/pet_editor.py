# utils/pet_editor.py

from utils.logging_utils import log_action
import json

PET_FILE = "pets.json"

def load_pets():
    """Load pet data from JSON file."""
    try:
        with open(PET_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_pets(pets):
    """Save pet data to JSON file."""
    with open(PET_FILE, "w") as f:
        json.dump(pets, f, indent=4)

def edit_pet(pet_name):
    """Edit an existing pet's details safely with confirmation."""
    pets = load_pets()
    pet = next((p for p in pets if p["name"].lower() == pet_name.lower()), None)

    if not pet:
        print(f"No pet found with the name '{pet_name}'.")
        return

    print(f"\nEditing {pet['name']}'s details. Press Enter to keep current value. Type 'cancel' at any time to abort.\n")

    changes = {}

    # Edit name
    new_name = input(f"Name [{pet['name']}]: ").strip()
    if new_name.lower() == "cancel":
        print("Edit cancelled.\n")
        return
    if new_name and new_name != pet['name']:
        changes['name'] = (pet['name'], new_name)

    # Edit weight
    while True:
        new_weight = input(f"Weight in kg [{pet['weight']}]: ").strip()
        if new_weight.lower() == "cancel":
            print("Edit cancelled.\n")
            return
        if not new_weight:
            break
        try:
            new_weight_val = float(new_weight)
            if new_weight_val != pet['weight']:
                changes['weight'] = (pet['weight'], new_weight_val)
            break
        except ValueError:
            print("Please enter a valid number or 'cancel' to abort.")

    # Edit calorie target
    while True:
        new_calories = input(f"Daily calorie target [{pet['calorie_target']}]: ").strip()
        if new_calories.lower() == "cancel":
            print("Edit cancelled.\n")
            return
        if not new_calories:
            break
        try:
            new_calories_val = float(new_calories)
            if new_calories_val != pet['calorie_target']:
                changes['calorie_target'] = (pet['calorie_target'], new_calories_val)
            break
        except ValueError:
            print("Please enter a valid number or 'cancel' to abort.")

    if not changes:
        print("No changes made.\n")
        return

    # Summary and confirmation
    print("\nReview changes:")
    for field, (old, new) in changes.items():
        print(f"- {field.capitalize()}: {old} → {new}")

    confirm = input("Apply these changes? (y/n): ").strip().lower()
    if confirm != "y":
        print("Edit cancelled.\n")
        return

    # Apply changes
    for field, (_, new_val) in changes.items():
        pet[field] = new_val
        log_action(f"Updated {field} for {pet['name']} to {new_val}")

    save_pets(pets)
    print(f"\n{pet['name']}'s details updated successfully!\n")