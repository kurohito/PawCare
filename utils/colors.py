# utils/colors.py
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def color_text(text, color):
    return f"{color}{text}{Colors.RESET}"