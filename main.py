import os
from utils.colors import Colors
from utils.pet_manager import load_pets, save_pets, add_pet, edit_pet, remove_pet
from utils.logging_utils import (
    log_feeding_entry,
    log_medication_entry,
    log_weight_entry,
    print_daily_summary,
    plot_weekly_weight_trend,
    manage_medications,
    manage_feeding_schedule,
    change_weight_unit,
    delete_all_data,
    reset_user_prefs,
    export_logs_to_csv,
    export_logs_to_json,
    view_upcoming_medications
)

def main():
    print(Colors.CYAN + "🐾 PET CARE TRACKER" + Colors.RESET)
    print("=" * 40)

    pets = load_pets()

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
            add_pet(pets)
            save_pets(pets)

        elif choice == "2":
            edit_pet(pets)
            save_pets(pets)

        elif choice == "3":
            remove_pet(pets)
            save_pets(pets)

        elif choice == "4":
            if not pets:
                print(Colors.YELLOW + "⚠️  No pets recorded." + Colors.RESET)
            else:
                print("\n" + "="*30)
                print("🐾 LIST OF ALL PETS")
                print("="*30)
                for name in pets.keys():
                    print(f"  - {name}")
                print("="*30)

        elif choice == "5":
            print("\n" + "="*50)
            print(Colors.BLUE + Colors.BOLD + "📝 LOG FOOD, MEDICATION, OR WEIGHT" + Colors.RESET)
            print("="*50)

            pet_name = select_pet(pets)  # Uses numbered selection — consistent UX
            if not pet_name:
                continue  # User canceled

            print("\nChoose an action:")
            print("1. Log Food")
            print("2. Log Medication")
            print("3. Log Weight")
            print("0. Back")
            sub_choice = input("Choose: ").strip()

            if sub_choice == "1":
                log_feeding_entry(pets)
            elif sub_choice == "2":
                log_medication_entry(pets)
            elif sub_choice == "3":
                log_weight_entry(pets)
            elif sub_choice == "0":
                continue
            else:
                print(Colors.RED + "❌ Invalid option." + Colors.RESET)

        elif choice == "6":
            print_daily_summary(pets)

        elif choice == "7":
            plot_weekly_weight_trend(pets)

        elif choice == "8":
            print("\nExport format:")
            print("1. CSV")
            print("2. JSON")
            fmt = input("Choose (1 or 2): ").strip()
            filename = input("Enter filename (e.g., logs): ").strip() or "logs"
            if fmt == "1":
                export_logs_to_csv(pets, f"{filename}.csv")
            elif fmt == "2":
                export_logs_to_json(pets, f"{filename}.json")
            else:
                print(Colors.RED + "❌ Invalid option." + Colors.RESET)

        elif choice == "9":
            view_upcoming_medications(pets)

        elif choice == "10":
            print("\n" + "="*30)
            print("SETTINGS")
            print("1. Change Weight Unit (kg/lb)")
            print("2. Delete All Data")
            print("3. Reset Preferences")
            print("0. Back")
            print("="*30)
            setting = input("Choose: ").strip()
            if setting == "1":
                change_weight_unit()
            elif setting == "2":
                delete_all_data()
                pets = load_pets()  # Reload empty pets
            elif setting == "3":
                reset_user_prefs()
            elif setting == "0":
                continue
            else:
                print(Colors.RED + "❌ Invalid option." + Colors.RESET)

        elif choice == "0":
            print(Colors.GREEN + "👋 Goodbye!" + Colors.RESET)
            break

        else:
            print(Colors.RED + "❌ Invalid choice. Try again." + Colors.RESET)

# --- HELPER: select_pet() ---
def select_pet(pets):
    """
    Displays numbered list of pets and returns the chosen pet name.
    Returns None if no pets or invalid selection.
    """
    if not pets:
        print(Colors.YELLOW + "⚠️  No pets available. Add a pet first." + Colors.RESET)
        return None

    print("\n" + "="*40)
    print(Colors.BLUE + "🐾 SELECT A PET" + Colors.RESET)
    print("="*40)

    pet_list = list(pets.keys())
    for i, name in enumerate(pet_list, 1):
        print(f"{i}. {name}")

    print("0. Cancel")
    print("-" * 40)

    try:
        choice = int(input("Choose pet by number: ").strip())
        if choice == 0:
            return None
        if 1 <= choice <= len(pet_list):
            return pet_list[choice - 1]
        else:
            print(Colors.RED + "❌ Invalid selection." + Colors.RESET)
            return None
    except ValueError:
        print(Colors.RED + "❌ Please enter a number." + Colors.RESET)
        return None

if __name__ == "__main__":
    main()