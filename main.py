import json
from datetime import datetime
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication

DATA_FILE = "pets.json"

# Load existing pet data
def load_pets():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save pet data
def save_pets(pets):
    with open(DATA_FILE, "w") as f:
        json.dump(pets, f, indent=4)

# Add a new pet
def add_pet(pets):
    name = input("Pet name: ")
    weight = float(input("Weight (kg): "))
    cal_target = float(input("Daily calorie target: "))
    cal_per_100g = float(input("Food calories per 100g: "))
    pet = {
        "name": name,
        "weight": weight,
        "cal_target": cal_target,
        "cal_per_100g": cal_per_100g,
        "feedings": [],
        "medications": []
    }
    pets.append(pet)
    save_pets(pets)
    print(f"🌸 {name} added!\n")

# Log feeding
def log_feeding(pets):
    if not pets:
        print("No pets yet. Add a pet first.\n")
        return

    for i, pet in enumerate(pets):
        print(f"{i + 1}. {pet['name']}")
    choice = int(input("Select pet by number: ")) - 1
    pet = pets[choice]

    grams = float(input("Grams fed: "))
    calories = calculate_calories(grams, pet["cal_per_100g"])
    time = datetime.now().strftime("%H:%M")
    pet["feedings"].append({"grams": grams, "calories": calories, "time": time})
    save_pets(pets)
    print(f"🍽 Logged feeding for {pet['name']} — {calories} cal at {time}\n")

# Log medication
def log_med(pets):
    if not pets:
        print("No pets yet. Add a pet first.\n")
        return

    for i, pet in enumerate(pets):
        print(f"{i + 1}. {pet['name']}")
    choice = int(input("Select pet by number: ")) - 1
    pet = pets[choice]

    med_name = input("Medication name: ")
    dose = input("Dose (e.g., 0.5ml): ")
    time = datetime.now().strftime("%H:%M")
    pet["medications"].append({"med_name": med_name, "dose": dose, "time": time})
    save_pets(pets)
    print(f"💊 Logged {med_name} ({dose}) for {pet['name']} at {time}\n")

# Daily summary
def daily_summary(pets):
    if not pets:
        print("No pets yet.\n")
        return
    for pet in pets:
        print(f"--- {pet['name']} ---")
        total_cal = sum(f["calories"] for f in pet["feedings"])
        print(f"Calories today: {total_cal}/{pet['cal_target']} cal")
        print("Medications given today:")
        for med in pet["medications"]:
            print(f" - {med['med_name']} ({med['dose']}) at {med['time']}")
        print()

# CLI loop
def main():
    pets = load_pets()
    while True:
        print("🌸 PawCare Tracker 🌸")
        print("1. Add pet")
        print("2. Log feeding")
        print("3. Log medication")
        print("4. Daily summary")
        print("5. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            add_pet(pets)
        elif choice == "2":
            log_feeding(pets)
        elif choice == "3":
            log_med(pets)
        elif choice == "4":
            daily_summary(pets)
        elif choice == "5":
            print("Goodbye! 🌸")
            break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()