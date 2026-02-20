# utils/pet_manager.py
import json
import os
from utils.colors import Colors

PETS_FILE = "data/pets.json"

def load_pets() -> dict:
    """Load pets from JSON file. Return empty dict if file doesn't exist or is invalid."""
    if not os.path.exists(PETS_FILE):
        return {}
    try:
        with open(PETS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        print(Colors.RED + "⚠️  Corrupted pets data. Starting fresh." + Colors.RESET)
        return {}

def save_pets(pets: dict) -> None:
    """Save pets to JSON file. Create directory if needed."""
    os.makedirs("data", exist_ok=True)
    with open(PETS_FILE, "w") as f:
        json.dump(pets, f, indent=2)

def add_pet(pets: dict) -> None:
    """Interactive pet addition via console prompts."""
    print("\n" + "="*40)
    print(Colors.BLUE + "🐾 ADD A NEW PET" + Colors.RESET)
    print("="*40)
    
    name = input("Enter pet name: ").strip()
    if not name:
        print(Colors.RED + "❌ Pet name cannot be empty!" + Colors.RESET)
        return

    if name in pets:
        print(Colors.YELLOW + f"⚠️  Pet '{name}' already exists." + Colors.RESET)
        return

    species = input("Species (e.g., dog, cat): ").strip()
    if not species:
        species = "Unknown"

    breed = input("Breed (optional): ").strip() or "Unknown"
    birth_year = input("Birth year (optional): ").strip() or "Unknown"
    color = input("Color (optional): ").strip() or "Unknown"
    cal_input = input("Calories per 100g (for food tracking, optional): ").strip()
    calories_per_100g = float(cal_input) if cal_input else None

    pets[name] = {
        "species": species,
        "breed": breed,
        "birth_year": birth_year,
        "color": color,
        "calories_per_100g": calories_per_100g,
        "feedings": [],
        "medications": [],
        "weights": []
    }

    print(Colors.GREEN + f"✅ Pet '{name}' added successfully!" + Colors.RESET)

def edit_pet(pets: dict) -> None:
    """Interactive pet editing via numbered selection."""
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to edit. Add one first." + Colors.RESET)
        return

    print("\n" + "="*40)
    print(Colors.BLUE + "🐾 EDIT A PET" + Colors.RESET)
    print("="*40)

    pet_list = list(pets.keys())
    for i, name in enumerate(pet_list, 1):
        print(f"{i}. {name}")

    try:
        choice = int(input("Choose pet to edit: ")) - 1
        if choice < 0 or choice >= len(pet_list):
            raise ValueError
        pet_name = pet_list[choice]
    except (ValueError, IndexError):
        print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
        return

    pet = pets[pet_name]
    print(f"\nEditing: {pet_name}")
    print(f"Current: {pet}")

    pet["species"] = input(f"Species (current: {pet['species']}): ").strip() or pet["species"]
    pet["breed"] = input(f"Breed (current: {pet['breed']}): ").strip() or pet["breed"]
    pet["birth_year"] = input(f"Birth year (current: {pet['birth_year']}): ").strip() or pet["birth_year"]
    pet["color"] = input(f"Color (current: {pet['color']}): ").strip() or pet["color"]

    cal_input = input(f"Calories per 100g (current: {pet['calories_per_100g']}): ").strip()
    pet["calories_per_100g"] = float(cal_input) if cal_input else pet["calories_per_100g"]

    print(Colors.GREEN + "✅ Pet updated!" + Colors.RESET)

def remove_pet(pets: dict) -> None:
    """Interactive pet removal with confirmation."""
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to remove." + Colors.RESET)
        return

    print("\n" + "="*40)
    print(Colors.BLUE + "🐾 REMOVE A PET" + Colors.RESET)
    print("="*40)

    pet_list = list(pets.keys())
    for i, name in enumerate(pet_list, 1):
        print(f"{i}. {name}")

    try:
        choice = int(input("Choose pet to remove: ")) - 1
        if choice < 0 or choice >= len(pet_list):
            raise ValueError
        pet_name = pet_list[choice]
    except (ValueError, IndexError):
        print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
        return

    confirm = input(f"⚠️  Are you sure you want to delete '{pet_name}' and ALL its data? (y/N): ").strip().lower()
    if confirm != 'y':
        print(Colors.YELLOW + "❌ Deletion cancelled." + Colors.RESET)
        return

    del pets[pet_name]
    print(Colors.GREEN + f"✅ Pet '{pet_name}' and all data removed." + Colors.RESET)