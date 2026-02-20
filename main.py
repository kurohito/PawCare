import json
from utils.logging_utils import (
    log_feeding_entry,
    log_medication_entry,
    log_weight_entry,
    print_daily_summary,
    plot_weight_graph,
    plot_weekly_weight_trend,
    log_action,
    calculate_recent_weight_change,
)
from utils.calorie_calculator import calculate_calories
from utils.medication import log_medication
from utils.pet_editor import edit_pet

# --- ANSI colors for warnings and highlights ---
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    END = "\033[0m"

def color_text(text, color):
    return f"{color}{text}{Colors.END}"

PETS_FILE = "pets.json"

# --- Load pets ---
try:
    with open(PETS_FILE, "r", encoding="utf-8") as f:
        pets = json.load(f)
        if isinstance(pets, list):
            pets = {str(i+1): pet for i, pet in enumerate(pets)}
except FileNotFoundError:
    pets = {}

# --- Helper Functions ---
def save_pets():
    with open(PETS_FILE, "w", encoding="utf-8") as f:
        json.dump(pets, f, indent=2, ensure_ascii=False)

def confirm_action(message):
    while True:
        response = input(f"{message} (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            return True
        elif response in ["no", "n"]:
            print("Action cancelled.\n")
            return False
        else:
            print("Please type 'yes' or 'no'.")

def find_pet_by_name():
    name = input("Enter pet name to search: ").strip()
    for pet in pets.values():
        if pet["name"].lower() == name.lower():
            print(f"✅ Found: {pet['name']}")
            # Auto warnings
            total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
            target = pet.get("calorie_target", 0)
            if total_cal < target:
                print(color_text(f"⚠️ {pet['name']} calories below target today: {total_cal}/{target}", Colors.RED))
            weekly_change = calculate_recent_weight_change(pet)
            if abs(weekly_change) >= 5:
                print(color_text(f"⚠️ Rapid weight change in last 7 days: {weekly_change:+.1f}%", Colors.RED))
            return pet
    print(color_text("⚠️ Pet not found.", Colors.RED))
    return None

# --- Mini-sparkline generator ---
def mini_sparkline(pet, width=20):
    """Return a string with colored sparkline for daily summary."""
    history = pet.get("weight_history", [])
    if len(history) < 2:
        return ""
    weights = [h["weight"] for h in history[-width:]]
    spark = ""
    prev = None
    for w in weights:
        if prev is None:
            color = Colors.YELLOW
        elif w > prev:
            color = Colors.GREEN
        elif w < prev:
            color = Colors.RED
        else:
            color = Colors.YELLOW
        spark += color_text("▇", color)
        prev = w
    return spark

# --- Main loop ---
def main():
    while True:
        print("""
╔═══════════════════════════════════════════╗
 🌸🐾   P a w C a r e   T r a c k e r 🐾🌸
╚═══════════════════════════════════════════╝

1️⃣ Add Pet
2️⃣ Edit Pet
3️⃣ Search Pet by Name
4️⃣ Log Feeding
5️⃣ Log Medication
6️⃣ Log Weight
7️⃣ Daily Summary
8️⃣ Weight Graph
9️⃣ Weekly Weight Trend
🔟 Delete All Data
0️⃣ Exit
""")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            name = input("Pet name: ").strip()
            weight = float(input("Weight (kg): "))
            cal_target = int(input("Daily calorie target: "))
            cal_density = int(input("Food calorie density per 100g: "))
            pet_id = str(max([int(k) for k in pets.keys()] + [0]) + 1)
            pets[pet_id] = {
                "name": name,
                "weight": weight,
                "calorie_target": cal_target,
                "calorie_density": cal_density,
                "feedings": [],
                "medications": [],
                "weight_history": []
            }
            save_pets()
            log_action(f"🐾 Added new pet: {name}")
            print(color_text(f"✅ {name} added!\n", Colors.GREEN))

        elif choice == "2":
            pet = find_pet_by_name()
            if pet and confirm_action(f"✏️ Are you sure you want to edit {pet['name']}?"):
                edit_pet(pet)
                save_pets()
                log_action(f"✏️ Edited pet: {pet['name']}")
                print(color_text(f"✅ {pet['name']} updated.\n", Colors.GREEN))

        elif choice == "3":
            pet = find_pet_by_name()
            if pet:
                print()  # newline after warnings

        elif choice == "4":
            pet = find_pet_by_name()
            if pet:
                grams = float(input("Grams fed: "))
                log_feeding_entry(pet, grams)
                save_pets()
                 # Below target calories
                total_cal = sum(f.get("calories", 0) for f in pet.get("feedings", []))
                if total_cal < pet.get("calorie_target", 0):
                    print(color_text(f"⚠️ Feeding below daily calorie target! ({total_cal}/{pet['calorie_target']})", Colors.RED))
                print(color_text(f"✅ Feeding logged for {pet['name']}.\n", Colors.GREEN))

        elif choice == "5":
            pet = find_pet_by_name()
            if pet:
                med_name = input("Medication name: ").strip()
                dose = input("Dose: ").strip()
                if confirm_action(f"💊 Log {dose} of {med_name} for {pet['name']}?"):
                    log_medication_entry(pet, med_name, dose)
                    save_pets()
                    print(color_text(f"✅ Medication logged for {pet['name']}.\n", Colors.GREEN))

        elif choice == "6":
            pet = find_pet_by_name()
            if pet:
                weight = float(input("Enter new weight (kg): "))
                if confirm_action(f"⚖️ Log new weight {weight}kg for {pet['name']}?"):
                    log_weight_entry(pet, weight)
                    save_pets()
                    print(color_text(f"✅ Weight logged for {pet['name']}.\n", Colors.GREEN))
                    weekly_change = calculate_recent_weight_change(pet)
                    if abs(weekly_change) >= 5:
                        print(color_text(f"⚠️ Rapid weight change in last 7 days: {weekly_change:+.1f}%\n", Colors.RED))

        elif choice == "7":
            pet = find_pet_by_name()
            if pet:
                print_daily_summary(pet)
                spark = mini_sparkline(pet)
                if spark:
                    print(f"📈 Weight trend: {spark}\n")

        elif choice == "8":
            pet = find_pet_by_name()
            if pet:
                plot_weight_graph(pet)

        elif choice == "9":
            pet = find_pet_by_name()
            if pet:
                print(color_text("Legend: 🟢 Up  ➖ Same  🔻 Down  ▇ Weight bar", Colors.CYAN))
                plot_weekly_weight_trend(pet)

        elif choice == "10":
            if confirm_action("⚠️ Are you sure you want to DELETE ALL DATA? This cannot be undone."):
                if confirm_action("❗ Please confirm AGAIN to permanently delete all data."):
                    pets.clear()
                    save_pets()
                    log_action("🗑️ All data deleted")
                    print(color_text("✅ All data deleted!\n", Colors.RED))

        elif choice == "0":
            print("Goodbye! 🌸")
            break

        else:
            print(color_text("⚠️ Invalid choice. Try again.\n", Colors.RED))


if __name__ == "__main__":
    main()