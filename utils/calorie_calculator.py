# utils/calorie_calculator.py
def calculate_calories(grams, cal_per_100g):
    """
    Calculate calories from food weight and calorie density per 100g.
    
    Args:
        grams (float): Weight of food in grams
        cal_per_100g (float): Calories per 100 grams of food
    
    Returns:
        float: Calculated calories rounded to 2 decimals, or 0.0 on error
    """
    try:
        # Validate inputs
        if not isinstance(grams, (int, float)) or not isinstance(cal_per_100g, (int, float)):
            print("⚠️ Error: grams and cal_per_100g must be numbers.")
            return 0.0
        if grams < 0:
            print("⚠️ Warning: Negative grams entered. Using 0.")
            grams = 0
        if cal_per_100g <= 0:
            print("⚠️ Error: Calorie density must be greater than 0.")
            return 0.0
        calories = (grams / 100) * cal_per_100g
        return round(calories, 2)
    except Exception as e:
        print(f"⚠️ Unexpected error in calorie calculation: {e}")
        return 0.0