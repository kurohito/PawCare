from datetime import datetime
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
    manage_feeding_schedule,
    export_logs_to_csv,
    export_logs_to_json,
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

    # Ask for species
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

    # Calculate NRC target calories
    rerr = 70 * (weight ** 0.75)
    target_calories = int(rerr * 1.2)

    print(f"\n💡 Based on NRC 2006 veterinary guidelines:")
    print(f"   RER = 70 × ({weight} kg)^0.75 = {rerr:.1f} kcal")
    print(f"   MER (normal adult) = RER × 1.2 = {target_calories} kcal/day")
    print(f"   (Source: National Research Council — Nutrient Requirements of Dogs and Cats)")

    # Initialize pet with all required keys for new system
    pets[name] = {
        "species": species,
        "weight": weight,
        "target_daily_calories": target_calories,
        "medications": [],
        "feedings": [],
        "weights": [],
        "feeding_schedule": [],
        "feeding_reminders": False,
        "calories_per_100g": None,  # 👈 Required for auto-calculations
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
    print("4. Set Food Energy (kcal/100g) — For Auto-Calculating Feedings")  # 👈 NEW
    print("5. Add Feeding Log (manual)")
    print("6. Add Weight Log (manual)")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        medication = input("Medication name: ").strip()
        if not medication:
            print(Colors.RED + "❌ Medication name cannot be empty!" + Colors.RESET)
            return
        dose = input("Dose (e.g., 0.5ml per ear): ").strip()
        if not dose:
            print(Colors.RED + "❌ Dose cannot be empty!" + Colors.RESET)
            return
        notes = input("📝 Optional notes (press Enter to skip): ").strip() or ""

        # Add using new format
        pet["medications"].append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "medication": medication,
            "dose": dose,
            "notes": notes,
            "frequency": "one_time",
            "interval_hours": None,
            "dosing_time": None,
            "next_due": None,
            "reminder_enabled": False
        })
        print(Colors.GREEN + f"✅ Medication '{medication}' added!" + Colors.RESET)

    elif choice == "2":
        if not pet["medications"]:
            print(Colors.YELLOW + "⚠️  No medications to remove." + Colors.RESET)
            return
        print("\nAvailable medications:")
        for i, med in enumerate(pet["medications"], 1):
            freq = med.get("frequency", "one_time")
            if freq == "one_time":
                interval = " (One-time)"
            elif med.get("interval_hours"):
                interval = f" (Every {med['interval_hours']}h)"
            else:
                freq_labels = {"every_day": "Daily", "every_3_days": "Every 3 days", "weekly": "Weekly"}
                interval = f" ({freq_labels.get(freq, freq.replace('_', ' ').title())})"
            print(f"{i}. {med['medication']} — {med['dose']}{interval}")
        try:
            idx = int(input("Enter number to remove: ")) - 1
            if 0 <= idx < len(pet["medications"]):
                removed = pet["medications"].pop(idx)
                print(Colors.GREEN + f"✅ Removed: {removed['medication']}" + Colors.RESET)
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

    elif choice == "4":  # 👈 NEW: Set calories per 100g
        while True:
            try:
                cals_input = input("Enter calories per 100g of food (e.g., 350): ").strip()
                if cals_input == "":
                    print(Colors.RED + "❌ This is required for auto-calculating feedings." + Colors.RESET)
                    continue
                calories_per_100g = float(cals_input)
                if calories_per_100g <= 0:
                    print(Colors.RED + "❌ Must be greater than 0." + Colors.RESET)
                    continue
                pet["calories_per_100g"] = calories_per_100g
                print(Colors.GREEN + f"✅ Food energy set to {calories_per_100g} kcal per 100g!" + Colors.RESET)
                break
            except ValueError:
                print(Colors.RED + "❌ Invalid number. Enter a value like 350." + Colors.RESET)

    elif choice == "5":
        grams = float(input("Enter food amount in grams: "))
        # 👇 Now we let logging_utils auto-calculate if calories_per_100g is set
        calories = None  # Let log_feeding_entry handle it
        log_feeding_entry(pets, name, grams, calories)
        print(Colors.GREEN + "✅ Feeding logged!" + Colors.RESET)

    elif choice == "6":
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
        cals = data.get("calories_per_100g", "Not set")
        print(f"  - {name}: {meds} meds, {feedings} feedings, {weights} weights | Food: {cals} kcal/100g")


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

    # Show food energy if set
    cals_per_100g = pet.get("calories_per_100g")
    if cals_per_100g:
        print(f"📦 Food energy: {cals_per_100g} kcal per 100g")
    else:
        print(f"📦 Food energy: Not set — use Edit Pet to set it for auto-calculations")

    print(f"\nLogging for {name}:")
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
            freq = med.get("frequency", "one_time")
            if freq == "one_time":
                interval = " (One-time)"
            elif med.get("interval_hours"):
                interval = f" (Every {med['interval_hours']}h)"
            else:
                freq_labels = {"every_day": "Daily", "every_3_days": "Every 3 days", "weekly": "Weekly"}
                interval = f" ({freq_labels.get(freq, freq.replace('_', ' ').title())})"
            print(f"{i}. {med['medication']} — {med['dose']}{interval}")
        try:
            idx = int(input("Select medication (number): ")) - 1
            if 0 <= idx < len(meds):
                medication = meds[idx]["medication"]
                dose = meds[idx]["dose"]
                notes = meds[idx].get("notes", "")
                log_medication_entry(pets, name, medication, dose, notes)  # 👈 Fixed signature
                print(Colors.GREEN + "✅ Medication logged!" + Colors.RESET)
            else:
                print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
        except ValueError:
            print(Colors.RED + "❌ Invalid input." + Colors.RESET)

    elif choice == "2":
        grams = float(input("Enter food amount in grams: "))
        # Let logging_utils auto-calculate if calories_per_100g is set
        calories = None
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
        print("8. Export Logs (CSV/JSON)")
        print("9. View Upcoming Medications")
        print("10. Settings")
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
            print("\n" + "="*50)
            print("📤 EXPORT LOGS")
            print("1. Export to CSV")
            print("2. Export to JSON")
            print("0. Back")
            print("="*50)
            sub_choice = input("Choose export format: ").strip()

            if sub_choice == "1":
                export_logs_to_csv(load_pets(), "logs_export.csv")
                input("Press Enter to return...")
            elif sub_choice == "2":
                export_logs_to_json(load_pets(), "logs_export.json")
                input("Press Enter to return...")
            elif sub_choice == "0":
                pass
            else:
                print(Colors.RED + "❌ Invalid option." + Colors.RESET)
                input("Press Enter to return...")
        elif choice == "9":
            pets = load_pets()
            view_upcoming_medications(pets)
        elif choice == "10":
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
                    manage_feeding_schedule(load_pets())
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