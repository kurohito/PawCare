from utils.colors import Colors
from utils.logging_utils import (
    load_pets,
    save_pets,
    load_user_prefs,
    save_user_prefs,
    log_feeding_entry,
    log_medication_entry,
    log_weight_entry,
    view_upcoming_medications,
    print_daily_summary,
    plot_weekly_weight_trend,
    manage_medications,
    change_weight_unit,
    delete_all_data,
    reset_user_prefs,
    manage_feeding_schedule,  # ✅ NEW: Import for feeding schedule
)

def add_pet():
    pets = load_pets()
    name = input("Enter pet name: ").strip()
    if not name:
        print(Colors.RED + "❌ Pet name cannot be empty!" + Colors.RESET)
        return
    if name in pets:
        print(Colors.YELLOW + "⚠️  Pet already exists!" + Colors.RESET)
        return

    # Ask for species to determine typical weight range
    species = input("Enter species (cat/dog): ").strip().lower()
    if species not in ["cat", "dog"]:
        print(Colors.RED + "❌ Only 'cat' or 'dog' allowed." + Colors.RESET)
        return

    # Ask for weight in kg
    while True:
        try:
            weight = float(input(f"Enter {name}'s weight in kg: "))
            if weight <= 0:
                print(Colors.RED + "❌ Weight must be positive!" + Colors.RESET)
                continue
            break
        except ValueError:
            print(Colors.RED + "❌ Invalid weight. Enter a number (e.g., 4.2)." + Colors.RESET)

    # Calculate NRC target calories: RER = 70 × (weight^0.75), MER = RER × 1.2 (adult neutered)
    rerr = 70 * (weight ** 0.75)
    target_calories = int(rerr * 1.2)

    # Display calculation for transparency
    print(f"\n💡 Based on NRC 2006 veterinary guidelines:")
    print(f"   RER = 70 × ({weight} kg)^0.75 = {rerr:.1f} kcal")
    print(f"   MER (normal adult) = RER × 1.2 = {target_calories} kcal/day")
    print(f"   (Source: National Research Council — Nutrient Requirements of Dogs and Cats)")

    # Initialize pet with weight, target calories, and empty logs
    pets[name] = {
        "species": species,
        "weight": weight,
        "target_daily_calories": target_calories,
        "medications": [],
        "feedings": [],
        "weights": [],
        "feeding_schedule": [],      # ✅ Ensure keys exist for new system
        "feeding_reminders": False
    }

    save_pets(pets)
    print(Colors.GREEN + f"✅ Pet '{name}' ({species}) added with weight {weight} kg and target {target_calories} kcal/day!" + Colors.RESET)


def edit_pet():
    pets = load_pets()
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to edit. Add a pet first." + Colors.RESET)
        return
    print("\nAvailable pets:")
    for name in pets.keys():
        print(f"  - {name}")
    name = input("\nEnter pet name to edit: ").strip()
    if name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        return

    pet = pets[name]
    print(f"\nEditing: {name}")

    # If weight is missing, ask for it
    if "weight" not in pet or pet["weight"] is None:
        print(Colors.YELLOW + "⚠️  Weight not set. Please enter it now." + Colors.RESET)
        while True:
            try:
                weight = float(input(f"Enter {name}'s weight in kg: "))
                if weight <= 0:
                    print(Colors.RED + "❌ Weight must be positive!" + Colors.RESET)
                    continue
                pet["weight"] = weight
                rerr = 70 * (weight ** 0.75)
                pet["target_daily_calories"] = int(rerr * 1.2)
                print(f"💡 Auto-calculated target: {pet['target_daily_calories']} kcal/day (NRC 2006)")
                break
            except ValueError:
                print(Colors.RED + "❌ Invalid weight. Enter a number." + Colors.RESET)

    print("\nOptions:")
    print("1. Add Medication")
    print("2. Remove Medication")
    print("3. Update Weight (recalculates calories)")
    print("4. Add Feeding Log (manual)")
    print("5. Add Weight Log (manual)")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        med_name = input("Medication name: ").strip()
        dose = input("Dose (e.g., 0.5ml per ear): ").strip()
        interval_input = input("Repeat every ? hours (leave blank for one-time): ").strip()
        interval_hours = int(interval_input) if interval_input.isdigit() else None
        med = {
            "name": med_name,
            "dose": dose,
            "interval_hours": interval_hours,
            "next_due": "2026-01-01 00:00",  # placeholder
        }
        pet["medications"].append(med)
        print(Colors.GREEN + f"✅ Medication '{med_name}' added!" + Colors.RESET)

    elif choice == "2":
        if not pet["medications"]:
            print(Colors.YELLOW + "⚠️  No medications to remove." + Colors.RESET)
            return
        for i, med in enumerate(pet["medications"], 1):
            interval = f" (Every {med['interval_hours']}h)" if med.get("interval_hours") else " (One-time)"
            print(f"{i}. {med['name']} — {med['dose']}{interval}")
        try:
            idx = int(input("Enter number to remove: ")) - 1
            if 0 <= idx < len(pet["medications"]):
                removed = pet["medications"].pop(idx)
                print(Colors.GREEN + f"✅ Removed: {removed['name']}" + Colors.RESET)
            else:
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
        except ValueError:
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "3":  # Update weight → recalculate calories
        while True:
            try:
                new_weight = float(input(f"Enter new weight for {name} (kg): "))
                if new_weight <= 0:
                    print(Colors.RED + "❌ Weight must be positive!" + Colors.RESET)
                    continue
                old_weight = pet["weight"]
                pet["weight"] = new_weight
                rerr = 70 * (new_weight ** 0.75)
                pet["target_daily_calories"] = int(rerr * 1.2)
                print(f"💡 Updated from {old_weight}kg → {new_weight}kg")
                print(f"   New target: {pet['target_daily_calories']} kcal/day (NRC 2006)")
                break
            except ValueError:
                print(Colors.RED + "❌ Invalid weight. Enter a number." + Colors.RESET)

    elif choice == "4":
        grams = float(input("Enter food amount in grams: "))
        calories = float(input("Enter calories: "))
        log_feeding_entry(pets, name, grams, calories)
        print(Colors.GREEN + "✅ Feeding logged!" + Colors.RESET)

    elif choice == "5":
        weight = float(input("Enter weight (kg): "))
        log_weight_entry(pets, name, weight)
        print(Colors.GREEN + "✅ Weight logged!" + Colors.RESET)

    else:
        print(Colors.RED + "❌ Invalid option." + Colors.RESET)
        return

    save_pets(pets)


def remove_pet():
    pets = load_pets()
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to remove." + Colors.RESET)
        return
    print("\nAvailable pets:")
    for name in pets.keys():
        print(f"  - {name}")
    name = input("\nEnter pet name to remove: ").strip()
    if name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        return
    confirm = input(f"⚠️  Are you sure you want to delete all data for '{name}'? (y/N): ").strip().lower()
    if confirm == 'y':
        del pets[name]
        save_pets(pets)
        print(Colors.GREEN + f"✅ Pet '{name}' and all associated data removed!" + Colors.RESET)
    else:
        print(Colors.YELLOW + "❌ Removal cancelled." + Colors.RESET)


def list_pets():
    pets = load_pets()
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets registered." + Colors.RESET)
        return
    print("\n🐾 Registered Pets:")
    for name, data in pets.items():
        meds = len(data.get("medications", []))
        feedings = len(data.get("feedings", []))
        weights = len(data.get("weights", []))
        print(f"  - {name}: {meds} meds, {feedings} feedings, {weights} weights")


def log_menu():
    pets = load_pets()
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets to log for. Add a pet first." + Colors.RESET)
        return
    print("\nAvailable pets:")
    for name in pets.keys():
        print(f"  - {name}")
    name = input("\nEnter pet name: ").strip()
    if name not in pets:
        print(Colors.RED + "❌ Pet not found!" + Colors.RESET)
        return

    pet = pets[name]
    # Show target if set
    if pet.get("target_daily_calories"):
        print(f"\n🎯 Target daily calories: {pet['target_daily_calories']} kcal (NRC 2006)")
    else:
        print(f"\n⚠️  No target calories set. Set weight in Edit Pet.")

    print(f"Logging for {name}:")
    print("1. Log Medication")
    print("2. Log Feeding")
    print("3. Log Weight")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        print("Available medications:")
        meds = pet.get("medications", [])
        if not meds:
            print(Colors.YELLOW + "⚠️  No medications set. Add one in Edit Pet." + Colors.RESET)
            return
        for i, med in enumerate(meds, 1):
            interval = f" (Every {med['interval_hours']}h)" if med.get("interval_hours") else " (One-time)"
            print(f"{i}. {med['name']} — {med['dose']}{interval}")
        try:
            idx = int(input("Select medication (number): ")) - 1
            if 0 <= idx < len(meds):
                dose = meds[idx]["dose"]
                log_medication_entry(pets, name, dose)
                print(Colors.GREEN + "✅ Medication logged!" + Colors.RESET)
            else:
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
        except ValueError:
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "2":
        grams = float(input("Enter food amount in grams: "))
        calories = float(input("Enter calories: "))
        log_feeding_entry(pets, name, grams, calories)
        print(Colors.GREEN + "✅ Feeding logged!" + Colors.RESET)

    elif choice == "3":
        weight = float(input("Enter weight (kg): "))
        log_weight_entry(pets, name, weight)
        print(Colors.GREEN + "✅ Weight logged!" + Colors.RESET)

    else:
        print(Colors.RED + "❌ Invalid option." + Colors.RESET)
        return

    save_pets(pets)


def main():
    print(Colors.BOLD + "🐾 Welcome to PawCare - Your Pet's Health Companion!" + Colors.RESET)

    while True:
        print("\n" + "="*50)
        print("MAIN MENU")
        print("1. Add Pet")
        print("2. Edit Pet")
        print("3. Remove Pet")
        print("4. List All Pets")
        print("5. Log Food/Meds/Weight")
        print("6. View Daily Summary")
        print("7. View Weekly Weight Trend")
        print("8. View Logs")
        print("9. Settings")
        print("0. Exit")
        print("="*50)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_pet()
        elif choice == "2":
            edit_pet()
        elif choice == "3":
            remove_pet()
        elif choice == "4":
            list_pets()
        elif choice == "5":
            log_menu()
        elif choice == "6":
            print_daily_summary(load_pets())
        elif choice == "7":
            plot_weekly_weight_trend(load_pets())
        elif choice == "8":
            print(Colors.YELLOW + "ℹ️  Logs are viewable in data/logs.json" + Colors.RESET)
            input("Press Enter to return...")
        elif choice == "9":
            while True:
                print("\n" + "="*56)
                print("⚙️  SETTINGS")
                print("1. Set Feeding Schedule (meals, calories, reminders)")
                print("2. Manage Medications (with time & repeating) (per pet)")
                print("3. Change Weight Unit (Current: " + load_user_prefs().get("unit", "kg").upper() + ")")
                print("4. View Upcoming Medications")
                print("5. Delete All Data (Clear Files)")
                print("6. Reset User Preferences")
                print("7. Back to Main Menu")
                print("="*56)
                sub_choice = input("Choose an option: ").strip()

                if sub_choice == "1":
                    manage_feeding_schedule(load_pets())  # ✅ NEW: Call feeding schedule manager
                elif sub_choice == "2":
                    manage_medications(load_pets())
                elif sub_choice == "3":
                    change_weight_unit()
                elif sub_choice == "4":
                    pets = load_pets()
                    view_upcoming_medications(pets)
                elif sub_choice == "5":
                    delete_all_data()
                elif sub_choice == "6":
                    reset_user_prefs()
                elif sub_choice == "7":
                    break
                else:
                    print(Colors.RED + "❌ Invalid option. Try again." + Colors.RESET)
        elif choice == "0":
            print(Colors.GREEN + "👋 Thank you for using PawCare!" + Colors.RESET)
            break
        else:
            print(Colors.RED + "❌ Invalid choice. Please try again." + Colors.RESET)


if __name__ == "__main__":
    main()