# utils/calorie_calculator.py

def calculate_calories(grams, cal_per_100g):
    """
    Calculate the calories for a given amount of food.
    
    Parameters:
    - grams (float): Amount of food fed in grams.
    - cal_per_100g (float): Calories per 100 grams of the food.

    Returns:
    - float: Calories for the given portion, rounded to 2 decimals.
    """
    try:
        calories = (grams / 100) * cal_per_100g
        return round(calories, 2)
    except TypeError:
        print("⚠️ Error: grams and cal_per_100g must be numbers.")
        return 0.0