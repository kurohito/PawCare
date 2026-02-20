def calculate_calories(grams, cal_per_100g):
    """
    Returns calories for a given food amount
    """
    return round((grams / 100) * cal_per_100g, 2)