# main.py
import json
from colorama import init, Fore, Style
from utils.logging_utils import (
    log_feeding_entry,
    log_medication_entry,
    print_daily_summary,
    log_weight_entry,
    plot_weight_graph
)

init(autoreset=True)  # Reset colors automatically

DATA_FILE = "pets.json"

# Load pets
def load_pets():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save pets
def save_pets(pets):
    with open(DATA_FILE, "w") as f:
        json.dump(pets, f, indent=4)

# Cute banner
def print_banner():
    print(Fore.MAGENTA + Style.BRIGHT + "\n🌸 PawCare Tracker 🌸")
    print(Fore.CYAN + "Because tiny creatures deserve organised love\n")

# Menu display
def print_menu():
    print(Fore.YELLOW + "1. Add pet")
    print(Fore.YELLOW + "2. Log feeding")
    print(Fore.YELLOW + "3. Log medication")
    print(Fore.YELLOW + "4. Daily summary")
    print(Fore.YELLOW + "5. Exit")
    print(Fore.YELLOW + "6. Log / View Weight History")

# Add pet
def add_pet(pets):
    print(Fore.MAGENTA + "\n🌸 Add a New Pet 🌸")
    name = input("Pet name: ")
    weight = float(input("Weight (kg): "))
    cal_target = float(input("Daily calorie target: "))
    cal_per_100g = float(input("Food calories per 100g: "))
    pet = {
        "name": name,
        "weight": weight,
        "weight_history": [{"date": "", "weight": weight}],
        "cal_target": cal_target,
        "cal_per_100g": cal_per_100g,
        "feedings": [],
        "medications": []
    }
    pets.append(pet)
    save_pets(pets)
    print(Fore.GREEN + f"🌟 {name} added!\n")

# Log feeding
def log_feeding(pets):
    if not pets:
        print(Fore.RED + "No pets yet. Add a pet first.\n")
        return
    print(Fore.CYAN + "\n🍽 Log Feeding")
    for i, pet in enumerate(pets):
        print(f"{i + 1}. {pet['name']}")
    choice = int(input("Select pet by number: ")) - 1
    pet = pets[choice]

    grams = float(input("Grams fed: "))
    entry = log_feeding_entry(pet, grams)
    save_pets(pets)

    progress = min(sum(f["calories"] for f in pet["feedings"]) / pet['cal_target'], 1.0)
    bar = "🌸" * int(progress * 20) + "💤" * (20 - int(progress * 20))
    print(Fore.GREEN + f"✅ Logged {entry['calories']} cal for {pet['name']} at {entry['time']}")
    print(Fore.MAGENTA + f"Calorie Progress: [{bar}] {int(progress*100)}%\n")

# Log medication
def log_med(pets):
    if not pets:
        print(Fore.RED + "No pets yet. Add a pet first.\n")
        return
    print(Fore.CYAN + "\n💊 Log Medication")
    for i, pet in enumerate(pets):
        print(f"{i + 1}. {pet['name']}")
    choice = int(input("Select pet by number: ")) - 1
    pet = pets[choice]

    med_name = input("Medication name: ")
    dose = input("Dose (e.g., 0.5ml): ")
    entry = log_medication_entry(pet, med_name, dose)
    save_pets(pets)
    print(Fore.GREEN + f"✅ Logged {med_name} ({dose}) for {pet['name']} at {entry['time']}\n")

# Daily summary
def daily_summary(pets):
    if not pets:
        print(Fore.RED + "No pets yet.\n")
        return
    print(Fore.MAGENTA + "\n🌸 Daily Summary 🌸\n")
    for pet in pets:
        print_daily_summary(pet)
        total_cal = sum(f["calories"] for f in pet.get("feedings", []))
        progress = min(total_cal / pet["cal_target"], 1.0)
        bar = "🌸" * int(progress * 20) + "💤" * (20 - int(progress * 20))
        print(Fore.CYAN + f"Calorie Progress: [{bar}] {int(progress*100)}%\n")

# Weight log & graph
def weight_menu(pets):
    if not pets:
        print(Fore.RED + "No pets yet. Add a pet first.\n")
        return
    for i, pet in enumerate(pets):
        print(f"{i + 1}. {pet['name']}")
    choice_pet = int(input("Select pet by number: ")) - 1
    pet = pets[choice_pet]

    print("\n1. Log new weight")
    print("2. Show weight graph")
    sub_choice = input("Choose an option: ")
    if sub_choice == "1":
        weight = float(input("Enter weight in kg: "))
        entry = log_weight_entry(pet, weight)
        save_pets(pets)
        print(Fore.GREEN + f"✅ Logged {weight} kg for {pet['name']} on {entry['date']}\n")
    elif sub_choice == "2":
        plot_weight_graph(pet)
    else:
        print(Fore.RED + "Invalid choice.\n")

# Main loop
def main():
    pets = load_pets()
    while True:
        print_banner()
        print_menu()
        choice = input("\nChoose an option: ")

        if choice == "1":
            add_pet(pets)
        elif choice == "2":
            log_feeding(pets)
        elif choice == "3":
            log_med(pets)
        elif choice == "4":
            daily_summary(pets)
        elif choice == "5":
            print(Fore.MAGENTA + "Goodbye! 🌸")
            break
        elif choice == "6":
            weight_menu(pets)
        else:
            print(Fore.RED + "Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()