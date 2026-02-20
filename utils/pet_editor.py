# utils/pet_editor.py
from utils.logging_utils import log_action
from datetime import datetime


def _validate_and_clean_times(times_list):
    """
    Validate HH:MM format, remove duplicates, and sort chronologically.
    """
    valid_times = []

    for t in times_list:
        try:
            datetime.strptime(t, "%H:%M")
            valid_times.append(t)
        except ValueError:
            print(f"⚠️ Invalid time skipped: {t}")

    # Remove duplicates
    valid_times = list(set(valid_times))

    # Sort times
    valid_times.sort(key=lambda x: datetime.strptime(x, "%H:%M"))

    return valid_times


def edit_pet(pet):
    """
    Edit a single pet dictionary safely.
    Allows editing: name, weight, calorie_target,
    calorie_density, feeding_schedule.
    """

    print(f"\nEditing {pet['name']}'s details.")
    print("Press Enter to keep current value.\n")

    changes = {}

    # --- Name ---
    new_name = input(f"Name [{pet['name']}]: ").strip()
    if new_name and new_name != pet['name']:
        changes['name'] = (pet['name'], new_name)

    # --- Weight ---
    while True:
        new_weight = input(f"Weight in kg [{pet['weight']}]: ").strip()
        if not new_weight:
            break
        try:
            new_weight_val = float(new_weight)
            if new_weight_val <= 0:
                print("⚠️ Weight must be positive.")
                continue
            if new_weight_val != pet['weight']:
                changes['weight'] = (pet['weight'], new_weight_val)
            break
        except ValueError:
            print("⚠️ Invalid number. Try again.")

    # --- Daily calorie target ---
    while True:
        new_cal = input(f"Daily calorie target [{pet['calorie_target']}]: ").strip()
        if not new_cal:
            break
        try:
            new_cal_val = int(new_cal)
            if new_cal_val <= 0:
                print("⚠️ Must be positive.")
                continue
            if new_cal_val != pet['calorie_target']:
                changes['calorie_target'] = (pet['calorie_target'], new_cal_val)
            break
        except ValueError:
            print("⚠️ Invalid number. Try again.")

    # --- Calorie density per 100g ---
    while True:
        new_density = input(f"Calorie density per 100g [{pet['calorie_density']}]: ").strip()
        if not new_density:
            break
        try:
            new_density_val = int(new_density)
            if new_density_val <= 0:
                print("⚠️ Must be positive.")
                continue
            if new_density_val != pet['calorie_density']:
                changes['calorie_density'] = (pet['calorie_density'], new_density_val)
            break
        except ValueError:
            print("⚠️ Invalid number. Try again.")

    # --- Feeding schedule ---
    edit_schedule = input("\nDo you want to edit feeding times? (yes/no): ").strip().lower()

    if edit_schedule in ['yes', 'y']:
        schedule = pet.get("feeding_schedule", [])
        print("Current feeding times (24h format):", schedule if schedule else "None")

        new_times = input(
            "Enter new feeding times, comma-separated (e.g., 09:00,13:00,18:00): "
        ).strip()

        if new_times:
            times_list = [t.strip() for t in new_times.split(",") if t.strip()]
            cleaned_times = _validate_and_clean_times(times_list)

            if cleaned_times:
                if cleaned_times != schedule:
                    changes['feeding_schedule'] = (schedule, cleaned_times)
            else:
                print("⚠️ No valid times entered. Schedule unchanged.")

    # --- Apply changes ---
    if not changes:
        print("\nNo changes made.\n")
        return

    print("\nReview changes:")
    for field, (old, new) in changes.items():
        print(f"- {field}: {old} → {new}")

    confirm = input("\nApply these changes? (y/n): ").strip().lower()
    if confirm != "y":
        print("Edit cancelled.\n")
        return

    for field, (_, new_val) in changes.items():
        pet[field] = new_val
        log_action(f"Updated {field} for {pet['name']} to {new_val}")

    print(f"\n✅ {pet['name']}'s details updated successfully!\n")