from colorama import Fore, Style, init


from utils import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    DEFAULT_PASSWORD_LENGTH,
    PasswordSettings,
    CHARACTER_TYPE_OPTIONS,
    clear_screen,
    random_password_generator,
    calculate_password_entropy,
    calculate_password_strength,
    evaluate_password_strength,
    enabled_character_types,
)


init(autoreset=True)


# ----------------------------- Constants ----------------------------- #
BORDER = '*' * 20
VALID_YES = {'y', ''}
VALID_NO = 'n'
MESSAGE_COLORS = {
    'prompt': Fore.CYAN,
    'error': Fore.RED,
    'end': Fore.GREEN,
}
COLOR_MAP = {
    'Very Weak': Fore.RED,
    'Weak': Fore.LIGHTRED_EX,
    'Fair': Fore.YELLOW,
    'Strong': Fore.MAGENTA,
    'Very Strong': Fore.GREEN,
}


# ----------------------------- Functions ----------------------------- #

def colorize_outputs(message_type: str, message_text: str) -> str:
    """Return a colorized version of a message based on its type."""
    color = MESSAGE_COLORS.get(message_type, '')
    return f'{color}{message_text}{Style.RESET_ALL}' if color else message_text


def ask_if_change_settings(settings: PasswordSettings) -> None:
    """Ask whether to change the default password settings."""
    while True:
        user_answer = input(
            colorize_outputs(
                'prompt',
                'Do you want to change the default settings? [Y/n]: '
            )
        ).strip().lower()

        if user_answer in VALID_YES:
            print('-' * 5, 'Changing default settings', '-' * 5, sep='')
            get_password_settings(settings)
            break
        if user_answer == VALID_NO:
            break
        print(
            colorize_outputs(
                "error",
                "Invalid input! Please enter 'y' for yes, 'n' for no, "
                "or press Enter to accept the default."
            )
        )


def get_user_password_length(
    option: str,
    default: int,
    min_length: int = MIN_PASSWORD_LENGTH,
    max_length: int = MAX_PASSWORD_LENGTH,
) -> int:
    """Prompt for a password length within the allowed range."""
    while True:
        user_input = input(
            colorize_outputs('prompt', f'{option} (Default is {default}) ')
        )

        if user_input == '':
            return default

        if user_input.isdigit():
            password_length = int(user_input)
            if min_length <= password_length <= max_length:
                return password_length

        print(
            colorize_outputs(
                'error',
                'Invalid input! '
                f'Password length must be between {min_length} and {max_length}. '
                'Please try again.'
            )
        )


def get_user_password_settings(option: str, default: bool) -> bool:
    """Prompt to include or exclude a character type."""
    while True:
        user_input = input(
            colorize_outputs(
                'prompt',
                f"Include {option}? [Y/n]: "
            )
        ).strip().lower()

        if user_input == '':
            return default
        if user_input in {'y', 'n'}:
            return user_input == 'y'

        print(colorize_outputs(
            "error", "Invalid input! Please enter 'y' or 'n'."
        ))


def get_password_settings(settings: PasswordSettings) -> None:
    """Update password settings until at least one character type is enabled."""
    default_settings = settings.copy()

    while True:
        for option, default in settings.items():
            if option == 'password_length':
                settings[option] = get_user_password_length(option, default)
            else:
                settings[option] = get_user_password_settings(option, default)

        if enabled_character_types(settings):
            return

        print(
            colorize_outputs(
                'error',
                'At least one character type must be selected. '
                'Please try again.'
            )
        )

        for option in CHARACTER_TYPE_OPTIONS:
            settings[option] = default_settings[option]


def get_generated_password(settings: PasswordSettings) -> str:
    """Generate a random password from the given settings."""
    return random_password_generator(settings)


def generate_password_with_metrics(
    settings: PasswordSettings,
) -> tuple[str, float, str]:
    """Generate a password along with its entropy and strength label."""
    password = get_generated_password(settings)
    entropy = calculate_password_entropy(password, settings)
    strength_data = evaluate_password_strength(entropy)

    return password, entropy, strength_data['label']


def colorize_strength(strength_label: str) -> str:
    """Colorize a strength label for console display."""
    for key, color in COLOR_MAP.items():
        if key.lower() in strength_label.lower():
            return f'{color}{strength_label}{Style.RESET_ALL}'
    return strength_label


def print_generated_password_entropy_strength(settings: PasswordSettings) -> None:
    """Print a generated password with entropy and strength."""
    try:
        password, entropy, strength = generate_password_with_metrics(settings)
    except ValueError as error:
        print(colorize_outputs('error', str(error)))
        return

    strength_label = colorize_strength(strength)
    print(BORDER)
    print(f"Generated password : {password}")
    print(f"Strength           : {strength_label}")
    print(f"Entropy            : {entropy:.2f} bits")
    print(BORDER)


def regenerate_random_password(settings: PasswordSettings) -> None:
    """Keep regenerating until the user declines."""
    while True:
        user_input = input(
            colorize_outputs(
                'prompt',
                'Regenerate? [Y/n]: '
            )
        ).strip().lower()

        if user_input in VALID_YES:
            print_generated_password_entropy_strength(settings)
        elif user_input == VALID_NO:
            print(colorize_outputs(
                'end', 'Password generator session ended. Goodbye! \n'
            ))
            break
        else:
            print(colorize_outputs(
                "error", "Invalid input! Please enter 'y' or 'n'."
            ))


def run(settings: PasswordSettings) -> None:
    """Run the CLI password generation workflow."""
    clear_screen()
    ask_if_change_settings(settings)
    print_generated_password_entropy_strength(settings)
    regenerate_random_password(settings)


if __name__ == "__main__":
    settings: PasswordSettings = {
        'password_length': DEFAULT_PASSWORD_LENGTH,
        'uppercase': True,
        'lowercase': True,
        'space': False,
        'minus': False,
        'underline': False,
        'digit': True,
        'symbol': True,
        'bracket': True,
    }

    run(settings)
