# utils/calorie_calculator.py

def calculate_calories(grams, cal_per_100g):
    try:
        calories = (grams / 100) * cal_per_100g
        return round(calories, 2)
    except TypeError:
        print("⚠️ Error: grams and cal_per_100g must be numbers.")
        return 0.0