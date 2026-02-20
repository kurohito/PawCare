# utils/colors.py
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    ENDC = "\033[0m"  # Alias for RESET for backward compatibility
    RESET = "\033[0m"
def color_text(text, color):
    """
    Apply color to text using ANSI escape codes.
    
    Args:
        text (str): Text to color
        color (str): Color constant from Colors class (e.g., Colors.RED)
    
    Returns:
        str: Colored text
    """
    return f"{color}{text}{Colors.RESET}"