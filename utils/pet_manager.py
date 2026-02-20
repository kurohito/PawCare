# utils/pet_manager.py
import json
import os
from typing import Dict, Any, List, Optional
def add_pet(pets: dict, name: str, weight: float, calorie_target: int, calorie_density: int, feeding_schedule: List[str], medication_times: List[str], feeding_reminder_enabled: bool = True, medication_reminder_enabled: bool = True) -> dict:
    pet_id = str(id({"name": name}))
    pets[pet_id] = {
        "name": name,
        "weight": weight,
        "calorie_target": calorie_target,
        "calorie_density": calorie_density,
        "feeding_schedule": feeding_schedule,
        "medication_times": medication_times,
        "feeding_reminder_enabled": feeding_reminder_enabled,
        "medication_reminder_enabled": medication_reminder_enabled,
        "quiet_hours": {},
        "snooze_until": None
    }
    return pets
def find_pet_by_name(pets: dict, name: str) -> Optional[str]:
    """
    Find a pet by name and return its ID. Returns None if not found.
    Case-insensitive match.
    """
    for pet_id, pet_data in pets.items():
        if pet_data.get("name", "").lower() == name.lower():
            return pet_id
    return None
def save_pets(pets: dict, filepath: str = "data/pets.json"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(pets, f, indent=2)
def load_pets(filepath: str = "data/pets.json") -> dict:
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)