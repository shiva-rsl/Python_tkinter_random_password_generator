import os
import math
import secrets
import string
from typing import TypedDict


# ----------------------------- Constants ----------------------------- #
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 30
DEFAULT_PASSWORD_LENGTH = 8

CHARSETS = {
    'uppercase': string.ascii_uppercase,
    'lowercase': string.ascii_lowercase,
    'digit': string.digits,
    'minus': '-',
    'underline': '_',
    'space': ' ',
    'symbol': """!?@#$%&*^~/\\|+=:;.,"'""",
    'bracket': '[]{}()<>',
}

DIGITS = CHARSETS['digit']
SYMBOLS = CHARSETS['symbol']
BRACKETS = CHARSETS['bracket']

PASSWORD_OPTION_RANGE_SIZE = {
    option: len(chars) for option, chars in CHARSETS.items()
}

STRENGTH_COLORS = {
    'very_weak': "#f01010",
    'weak': "#ed761c",
    'fair': "#EFE63E",
    'strong': "#e52bf2",
    'very_strong': "#06be06"
}

CHARACTER_TYPE_OPTIONS = tuple(CHARSETS.keys())


class PasswordSettings(TypedDict):
    """
    Settings used to generate a password.
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
    """Clear the terminal screen (CLI only)."""
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
    except Exception:
        print('\n' * 100)


def enabled_character_types(settings: PasswordSettings) -> list[str]:
    """Return the enabled character-type keys from settings."""
    return [
        option for option in CHARACTER_TYPE_OPTIONS
        if settings.get(option)
    ]


def build_character_pool(settings: PasswordSettings) -> str:
    """Return the combined character pool for the enabled options."""
    return ''.join(CHARSETS[option] for option in enabled_character_types(settings))


def _secure_shuffle(items: list[str]) -> None:
    """Shuffle a list in place using a cryptographically secure RNG."""
    for index in range(len(items) - 1, 0, -1):
        swap_index = secrets.randbelow(index + 1)
        items[index], items[swap_index] = items[swap_index], items[index]


def random_password_generator(settings: PasswordSettings) -> str:
    """
    Generate a password using a cryptographically secure RNG.

    When the password length permits, include at least one character
    from each enabled character type. Select remaining characters
    from the combined character pool, then shuffle the result.
    """
    password_length = settings['password_length']
    if not is_valid_password_length(password_length):
        raise ValueError(
            f'Password length must be between {MIN_PASSWORD_LENGTH} '
            f'and {MAX_PASSWORD_LENGTH} characters.'
        )

    selected_types = enabled_character_types(settings)
    if not selected_types:
        raise ValueError('At least one character type must be selected.')

    pool = build_character_pool(settings)
    password_chars: list[str] = []

    if password_length >= len(selected_types):
        password_chars.extend(
            secrets.choice(CHARSETS[option]) for option in selected_types
        )
        remaining = password_length - len(selected_types)
        password_chars.extend(secrets.choice(pool) for _ in range(remaining))
        _secure_shuffle(password_chars)
    else:
        password_chars.extend(secrets.choice(pool) for _ in range(password_length))

    return ''.join(password_chars)


def is_valid_password_length(password_length: int) -> bool:
    """Return True if password length is within the allowed range."""
    return MIN_PASSWORD_LENGTH <= password_length <= MAX_PASSWORD_LENGTH


def get_selected_password_length(password: str) -> int:
    """Return the number of characters in a password."""
    return len(password)


def analyze_selected_password(password: str) -> dict:
    """Detect which character types appear in a password."""
    return {
        'password_length': get_selected_password_length(password),
        **{
            option: any(character in chars for character in password)
            for option, chars in CHARSETS.items()
        },
    }


def calculate_password_range(settings: PasswordSettings) -> int:
    """Return the size of the character pool used for generation."""
    return len(build_character_pool(settings))


def calculate_password_entropy(
    password: str,
    settings: PasswordSettings,
) -> float:
    """
    Estimate password entropy in bits based on password length
    and the size of the enabled character pool.

    This is a simplified estimate that assumes each character
    is selected independently and uniformly from the same pool.
    It does not model the generator's mandatory character-type
    selection or the resulting output distribution.
    """
    character_pool = build_character_pool(settings)

    if len(character_pool) <= 1:
        return 0.0

    return len(password) * math.log2(len(character_pool))


def evaluate_password_strength(password_entropy: float) -> dict:
    """
    Classify estimated password entropy into strength levels.

    Entropy thresholds are based on the classification published by
    David Pleacher in "Password Entropy". The labels are adapted
    for this application and are not official NIST thresholds.
    """
    if password_entropy < 28:
        return {'score': 10, 'label': '🔴 Very Weak', 'color': STRENGTH_COLORS['very_weak']}
    if password_entropy < 36:
        return {'score': 30, 'label': '🟠 Weak', 'color': STRENGTH_COLORS['weak']}
    if password_entropy < 60:
        return {'score': 55, 'label': '🟡 Fair', 'color': STRENGTH_COLORS['fair']}
    if password_entropy < 128:
        return {'score': 80, 'label': '🟣 Strong', 'color': STRENGTH_COLORS['strong']}
    return {'score': 100, 'label': '🟢 Very Strong', 'color': STRENGTH_COLORS['very_strong']}


def calculate_password_strength(
    password: str,
    settings: PasswordSettings,
) -> tuple[int, str, str]:
    """Return (score, label, color) for a password and its settings."""
    password_entropy = calculate_password_entropy(password, settings)
    strength_data = evaluate_password_strength(password_entropy)
    return strength_data['score'], strength_data['label'], strength_data['color']
