import os
import re
import math
import secrets
import string
from typing import Sequence, TypedDict


# ----------------------------- Constants ----------------------------- #
DIGITS = '0123456789'
SYMBOLS = """!?@#$%&*^~/\|+=:;.,"'"""
BRACKETS = '[]{}()<>'
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 30
DEFAULT_PASSWORD_LENGTH = 8

# Password option ranges
PASSWORD_OPTION_RANGE_SIZE = {    
    'uppercase': 26, 
    'lowercase': 26, 
    'digit': 10, 
    'minus': 1, 
    'underline': 1, 
    'space': 1, 
    'symbol': 19, 
    'bracket': 8, 
}

# Colors
STRENGTH_COLORS = {
    'very_weak': "#f01010",
    'weak': "#ed761c",
    'fair': "#EFE63E",
    'strong': "#e52bf2",
    'perfect': "#06be06"
}


class PasswordSettings(TypedDict):
    """
    Represents the settings for generating a password.

    Attributes:
        password_length (int): Desired length of the generated password.
        uppercase (bool): Include uppercase letters if True.
        lowercase (bool): Include lowercase letters if True.
        space (bool): Include spaces if True.
        minus (bool): Include minus '-' characters if True.
        underline (bool): Include underline '_' characters if True.
        digit (bool): Include digits from the DIGITS string if True.
        symbol (bool): Include special symbols from the SYMBOLS string if True.
        bracket (bool): Include brackets from the BRACKETS string if True.
    """

    password_length: int
    uppercase: bool
    lowercase: bool
    space: bool
    minus: bool
    underline: bool
    digit: bool
    symbol: bool
    bracket: bool


def clear_screen() -> None:
    """
    Clears the terminal screen.

    Uses 'cls' command on Windows and 'clear' on Unix-based systems.
    If the command fails, it prints multiple newlines as a fallback.
    """
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        print('\n' * 100)


def generate_upper_case_char() -> str:
    """Return a random uppercase ASCII letter."""
    return secrets.choice(string.ascii_uppercase)


def generate_lower_case_char() -> str:
    """Return a random lowercase ASCII letter."""
    return secrets.choice(string.ascii_lowercase)


def generate_digit() -> str:
    """Return a random digit character from the DIGITS string."""
    return secrets.choice(DIGITS)


def generate_symbol() -> str:
    """Return a random symbol character from the SYMBOLS string."""
    return secrets.choice(SYMBOLS)


def generate_bracket() -> str:
    """Return a random bracket character from the BRACKET string."""
    return secrets.choice(BRACKETS)


def generated_password_char(settings: Sequence[str]) -> str:

    """
    Generate a random character based on enabled password settings.

    This function randomly selects one character type from the provided list 
    of enabled options (e.g., 'uppercase', 'digit', 'symbol') and returns a 
    randomly generated character of that type.

    Args:
        settings (Sequence[str]): 
            A sequence of enabled character types to choose from.

    Returns:
        str: A randomly generated character from the selected character type.

    Raises:
        ValueError: If an unsupported character type is encountered.
    """
    char_type = secrets.choice(settings)

    generators = {
        'uppercase': generate_upper_case_char,
        'lowercase': generate_lower_case_char,
        'bracket': generate_bracket,
        'symbol': generate_symbol,
        'digit': generate_digit,
        'space': lambda: ' ',
        'minus': lambda: '-',
        'underline': lambda: '_'
    }

    generator_func = generators.get(char_type)
    if not generator_func:
        raise ValueError(f"Unsupported character type: {char_type}")
    return generator_func()


def random_password_generator(settings: PasswordSettings) -> str:
    """
    Generates a random password based on the given settings.

    Args:
        settings (dict): A dictionary containing user preferences for
                         character types and password length.

    Returns:
        str: A randomly generated password.
    """

    password_length = settings['password_length']
    
    enabled_char_types = []
    all_options = ['uppercase', 'lowercase', 'space', 'minus', 'underline', 'digit', 'symbol', 'bracket']
    
    for option in all_options:
        if settings.get(option):
            enabled_char_types.append(option)

    password_chars = []
    for _ in range(password_length):
        password_chars.append(generated_password_char(enabled_char_types))

    return ''.join(password_chars)


def is_valid_password_length(password_length: int) -> bool:
    """
    Checks if the password length is valid (between 8 and 30).

    Args:
        `password_length` (int): The length to validate.

    Returns:
        bool: True if valid, otherwise False.
    """
    return MIN_PASSWORD_LENGTH <= password_length <= MAX_PASSWORD_LENGTH


def get_selected_password_length(password: str) -> int:
    """
    Evaluates the length of a given password.
    
    Args:
        password (str): The password to evaluate.

    Returns:
        int: The number of character in the password.
    """

    return len(password)


def analyze_selected_password(password: str) -> dict:
    """
    Analyzes a password to detect its characteristics.

    This function inspects the password for the presence of different 
    character types (uppercase, lowercase, digits, symbols, etc.) and 
    also records its length. The result is used in entropy and strength 
    calculations.

    Args:
        password (str): The password to evaluate.

    Returns:
        dict: A dictionary indicating the presence of character types and password length.
    """
    
    # selected_password = combobox_generated_password.get()
    length = get_selected_password_length(password)
    
    return {
        'password_length': length,
        'uppercase': bool(re.search(r"[A-Z]", password)),
        'lowercase': bool(re.search(r"[a-z]", password)),
        'digit': bool(re.search(r"[0-9]", password)),
        'minus': bool(re.search(r"-", password)),
        'underline': bool(re.search(r"_", password)),
        'space': bool(re.search(r"\s", password)),
        'symbol': bool(re.search(r"[!?@#$%&*^~/|:;.,'\"']", password)),
        'bracket': bool(re.search(r"[{}\[\]()<>]", password)),
    }


def calculate_password_range(password: str) -> int:
    """
    Determines the effective size of the character set used in a password.

    This function analyzes the given password to detect which character groups 
    (e.g., lowercase letters, uppercase letters, digits, symbols) are present.
    It then sums the predefined range sizes for each detected group.

    Args:
        password (str): The password to evaluate.

    Returns:
        int: Total character set size for entropy calculation.
    """
    
    password_range = 0
    password_features = analyze_selected_password(password)
    
    for key, value in password_features.items():
        if key != 'password_length' and value:
            password_range += PASSWORD_OPTION_RANGE_SIZE.get(key, 0)

    return password_range


def calculate_password_entropy(password: str, settings: PasswordSettings) -> float:
    """
    Calculates the entropy of a password based on its generation settings.

    Args:
        password (str): The generated password.
        settings (PasswordSettings): The settings used to generate the password.

    Returns:
        float: The calculated entropy of the generation process in bits.
    """

    password_length = get_selected_password_length(password)

    enabled_char_types = [
        option for option, enabled in settings.items()
        if option != 'password_length' and enabled
    ]

    category_count = len(enabled_char_types)

    entropy_per_character = math.log2(category_count) + (
        sum(
            math.log2(PASSWORD_OPTION_RANGE_SIZE[option])
            for option in enabled_char_types
        ) / category_count
    )

    return password_length * entropy_per_character


def evaluate_password_strength(password_entropy: float) -> dict:
    """
    Evaluates the strength of a password based on its entropy.

    Args:
        `password_entropy` (float): The entropy value of the password.

    Returns:
        dict: A dictionary containing the score, label and color representing the strength.
    """
    if password_entropy < 28:
        return {'score': 10, 'label': '🔴 Very Weak', 'color': STRENGTH_COLORS['very_weak']}
    elif password_entropy < 36:
        return {'score': 30, 'label': '🟠 Weak', 'color': STRENGTH_COLORS['weak']}
    elif password_entropy < 60:
        return {'score': 55, 'label': '🟡 Fair', 'color': STRENGTH_COLORS['fair']}
    elif password_entropy < 128:
        return {'score': 80, 'label': '🟣 Strong', 'color': STRENGTH_COLORS['strong']}
    else:
        return {'score': 100, 'label': '🟢 Perfect', 'color': STRENGTH_COLORS['perfect']}


def calculate_password_strength(
    password: str,
    settings: PasswordSettings
) -> tuple[int, str, str]:
    """
    Calculates the strength of a given password.

    Args:
        password (str): The Password to be evaluated.

    Returns:
        tuple[int, str, str]: A tuple containing:
            - score (int): Numerical strength score.
            - label (str): Human-readable description of strength (e.g., 'weak', 'strong')
            - color (str): Suggested color code for UI display.
    """
    password_entropy = calculate_password_entropy(password, settings)
    strength_date = evaluate_password_strength(password_entropy)
    return strength_date['score'], strength_date['label'], strength_date['color']
