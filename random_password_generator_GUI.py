import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename
from typing import Type, Dict, List, Any

from utils import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    CHARSETS,
    PasswordSettings,
    random_password_generator,
    is_valid_password_length,
    calculate_password_entropy,
    calculate_password_strength,
    enabled_character_types,
)


# ----------------------------- Constants ----------------------------- #

FONT_LARGE = ('Noto Sans', 20)
FONT_MEDIUM = ('Noto Sans', 15)
FONT_NORMAL = ('Noto Sans', 12)
FONT_SMALL = ('Noto Sans', 10)
FONT_BOLD = ('Noto Sans', 12, 'bold')

SOFTWARE_COLOR_BACKGROUND = '#DFE4E8'
COLOR_BACKGROUND = "#000000"
COLOR_FOREGROUND = "#F0CF28"

ABOUT_TEXT = '''The Random Password Generator enables you to generate secure and highly
    unpredictable passwords through an optional mix of lowercase and uppercase letters,
    numbers and special characters.'''

DEFAULT_CHECKED_TYPES = {'uppercase', 'lowercase', 'digit', 'symbol'}


# ----------------------------- Global Variables ----------------------------- #
checkbox_configs = []
password_history: List[Dict[str, Any]] = []
password_option: PasswordSettings = {}
labelframes = {}
checkboxes = {}
buttons = {}
labels = {}


# ----------------------------- Utility Functions ----------------------------- #

def show_checkbox_error_message() -> None:
    """Show an error popup if the user has not checked any character types."""
    messagebox.showinfo('Error', 'Please check at least one checkbox to proceed.')


def show_invalid_password_length_message() -> None:
    """Show an error popup if the password length is not valid."""
    messagebox.showinfo(
        'Error',
        f'Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters.'
    )


def get_spinbox_password_length() -> int:
    """Return the password length from the spinbox."""
    return int(spinbox_password_length.get())


def set_password_length() -> None:
    """Store a valid password length in `password_option`."""
    password_length = get_spinbox_password_length()
    if not is_valid_password_length(password_length):
        raise ValueError(
            f'Password length must be between {MIN_PASSWORD_LENGTH} '
            f'and {MAX_PASSWORD_LENGTH} characters.'
        )
    password_option['password_length'] = password_length


def get_selected_password() -> str:
    """Return the currently selected password from history."""
    selected_index = combobox_generated_password.current()

    if not 0 <= selected_index < len(password_history):
        return ''

    return password_history[selected_index]['password']


def get_settings_for_selected_password() -> PasswordSettings:
    """Return the settings used to generate the selected password."""
    selected_index = combobox_generated_password.current()

    if not 0 <= selected_index < len(password_history):
        return dict(password_option)

    return password_history[selected_index]['settings']
    

def show_password_entropy(settings: PasswordSettings) -> None:
    """Display the selected password's entropy."""
    selected_password = get_selected_password()
    password_entropy_value = calculate_password_entropy(selected_password, settings)
    labels['label_entropy_value'].config(text=f'{password_entropy_value:.2f} bits')


def update_password_strength_label(settings: PasswordSettings) -> None:
    """Update the password strength rating and color."""
    selected_password = get_selected_password()
    _, strength_level, strength_color = calculate_password_strength(selected_password, settings)
    labels['label_show_strength'].config(text=strength_level, fg=strength_color)


def get_password_options_from_user() -> None:
    """Update `password_option` from the current checkbox values."""
    for config in checkbox_configs:
        text = config['text']
        checkbox_name = re.sub(r'\s\(.*\)', '', text)
        password_option[checkbox_name.lower()] = config['variable'].get()


def generate_password() -> str:
    """Generate a password and store it with the settings used."""
    generated_password = random_password_generator(password_option)
    password_history.append({
        'password': generated_password,
        'settings': dict(password_option),
    })
    return generated_password


def show_generated_password_in_combobox() -> None:
    """Show generated passwords in the combobox and select the latest one."""
    passwords = [record['password'] for record in password_history]
    combobox_generated_password.config(values=passwords)
    combobox_generated_password.current(len(passwords) - 1)    


def show_password_strength_in_progressbar(settings: PasswordSettings) -> None:
    """Update the strength progress bar from the selected password."""
    selected_password = get_selected_password()
    strength, _, color = calculate_password_strength(selected_password, settings)
    style.configure('strength.Horizontal.TProgressbar', background=color)
    progressbar_generated_password.config(value=strength)


def update_password_strength_display(*args) -> None:
    """Refresh entropy, strength label, and progress bar."""
    selected_password = get_selected_password()
    if not selected_password:
        return
    settings = get_settings_for_selected_password()
    show_password_entropy(settings)
    update_password_strength_label(settings)
    show_password_strength_in_progressbar(settings)


def on_generate_password_click() -> None:
    """Handle the Generate Password button."""
    try:
        set_password_length()
    except ValueError:
        show_invalid_password_length_message()
        return

    get_password_options_from_user()

    if not enabled_character_types(password_option):
        show_checkbox_error_message()
        return

    generate_password()
    show_generated_password_in_combobox()
    update_password_strength_display()


def save_password_to_file() -> None:
    """Save generated passwords and handle file-related errors."""
    file_path = asksaveasfilename(
        title='Save Passwords',
        filetypes=[
            ('Text Document', '*.txt'),
            ('All Files', '*.*'),
        ],
        defaultextension='.txt',
    )

    if not file_path:
        return

    passwords = [
        record['password']
        for record in password_history
    ]

    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('\n'.join(passwords))

    except OSError as error:
        messagebox.showerror(
            'Save Error',
            f'Could not save passwords to the selected file.\n\n{error}',
        )
        return

    password_word = 'password' if len(passwords) == 1 else 'passwords'
    verb = 'was' if len(passwords) == 1 else 'were'

    messagebox.showinfo(
        'Save Successful',
        f'{password_word.capitalize()} {verb} saved successfully.',
    )


def show_save_error_if_empty(password: str) -> bool:
    """Return True if a password exists; otherwise show an error."""
    if not password:
        messagebox.showinfo('Error', 'There is nothing to be saved!')
        return False
    return True


def handle_save_password() -> None:
    """Validate, warn about plaintext storage, then save passwords."""
    generated_password = var.get()
    if not show_save_error_if_empty(generated_password):
        return

    should_save = messagebox.askokcancel(
        'Security Warning',
        'The passwords will be saved without encryption.\n\n'
        'Anyone who can access the file may be able to read '
        'the saved passwords.\n\n'
        'Do not use this feature to store your important '
        'real-world passwords in an unprotected file.\n\n'
        'Do you want to continue?',
        icon='warning',
    )
    if should_save:
        save_password_to_file()


def show_copy_error_if_empty(generated_password: str) -> bool:
    """Return True if the password is empty and an error was shown."""
    if not generated_password:
        messagebox.showinfo('Error', 'There is nothing to be copied!')
        return True
    return False


def show_copy_message() -> None:
    """Show a short confirmation after copying."""
    labels['label_guidance_text'].config(
        text='Password copied!',
        fg="#066A10"
    )
    window.after(2000, lambda: labels['label_guidance_text'].config(text=''))


def copy_to_clipboard() -> None:
    """Copy the selected password to the clipboard."""
    generated_password = var.get()

    if show_copy_error_if_empty(generated_password):
        return

    window.clipboard_clear()
    window.clipboard_append(generated_password)
    window.update_idletasks()
    show_copy_message()


def reset_password_ui() -> None:
    """Clear generated passwords and related displays."""
    password_history.clear()
    combobox_generated_password.set('')
    combobox_generated_password.config(values=())
    labels['label_entropy_value'].config(text='')
    labels['label_show_strength'].config(text='')
    progressbar_generated_password.config(value=0)


def toggle_about_text() -> None:
    """Show or hide the application description."""
    if not labels['label_guidance_text']['text'].strip():
        labels['label_guidance_text'].config(text=ABOUT_TEXT, fg=COLOR_BACKGROUND)
    else:
        labels['label_guidance_text'].config(text='')


def close_app() -> None:
    """Ask for confirmation, then close the application."""
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()


def _create_widget(
    widget_type: Type[tk.Widget],
    widget_config_list: List[Dict[str, Any]],
    widget_collection: Dict[str, tk.Widget]
) -> None:
    """Create and place widgets from configuration dictionaries."""
    supported_options = (
        'font',
        'text',
        'background',
        'foreground',
        'activebackground',
        'anchor',
        'command',
        'variable',
        'value',
    )

    for i, config in enumerate(widget_config_list):
        widget_kwargs = {
            option: config[option]
            for option in supported_options
            if option in config and config[option] is not None
        }
        widget = widget_type(master=config['master'], **widget_kwargs)
        widget.grid(**config['grid'])

        widget_name = config.get('name', f"{widget_type.__name__.lower()}_{i}")
        widget_collection[widget_name] = widget


def build_gui() -> tk.Tk:
    """Create and return the main application window."""
    global window, var, combobox_generated_password
    global spinbox_password_length, progressbar_generated_password, style

    window = tk.Tk()
    window.title('Random Password Generator App')
    window.config(bg=SOFTWARE_COLOR_BACKGROUND)
    window.geometry('700x840')
    window.resizable(width=False, height=False)

    window.columnconfigure(0, weight=1)
    window.columnconfigure(1, weight=2)
    window.columnconfigure(2, weight=1)

    labelframe_configs = [
        {
            'name': 'labelframe_settings',
            'master': window,
            'text': 'Password settings',
            'font': FONT_LARGE,
            'grid': {'row': 2, 'column': 0, 'columnspan': 5, 'padx': (10, 10), 'pady': (10, 0), 'sticky': 'EW'}
        },
        {
            'name': 'labelframe_generated_password',
            'master': window,
            'text': 'Generated Password(s)',
            'font': FONT_LARGE,
            'grid': {'row': 3, 'column': 0, 'ipadx': 120, 'ipady': 5, 'padx': (10, 10), 'pady': (10, 10)}
        },
        {
            'name': 'labelframe_buttons',
            'master': window,
            'grid': {'row': 4, 'column': 0, 'ipadx': 15, 'ipady': 0, 'padx': (10, 10), 'pady': (5, 10)}
        },
    ]

    _create_widget(tk.LabelFrame, labelframe_configs, labelframes)

    for col in range(3):
        labelframes['labelframe_settings'].columnconfigure(col, weight=1)

    label_configs = [
        {
            'name': 'label_title',
            'master': window,
            'text': 'Random Password Generator',
            'font': FONT_LARGE,
            'background': COLOR_BACKGROUND,
            'foreground': COLOR_FOREGROUND,
            'grid': {'row': 0, 'column': 0, 'columnspan': 5, 'ipadx': 250, 'ipady': 15, 'sticky': 'NSEW'},
        },
        {
            'name': 'label_subtitle',
            'master': window,
            'text': 'A free tool to quickly create your password',
            'font': FONT_NORMAL,
            'background': COLOR_BACKGROUND,
            'foreground': COLOR_FOREGROUND,
            'grid': {'row': 1, 'column': 0, 'columnspan': 5, 'ipady': 5, 'sticky': 'NEW'},
        },
        {
            'name': 'label_password_length',
            'master': labelframes['labelframe_settings'],
            'text': 'Length of generated password: ',
            'font': FONT_SMALL,
            'grid': {'row': 0, 'column': 0, 'padx': (30, 0), 'pady': (30, 30), 'sticky': 'w'},
        },
        {
            'name': 'label_password_length_numbers',
            'master': labelframes['labelframe_settings'],
            'text': f'({MIN_PASSWORD_LENGTH} to {MAX_PASSWORD_LENGTH} Chars)',
            'font': FONT_SMALL,
            'grid': {'row': 0, 'column': 2, 'padx': (0, 80), 'pady': (30, 30), 'sticky': 'w'},
        },
        {
            'name': 'label_random_password',
            'master': labelframes['labelframe_generated_password'],
            'text': 'Password: ',
            'font': FONT_MEDIUM,
            'grid': {'row': 0, 'column': 0, 'padx': 20, 'pady': 30, 'sticky': 'E'},
        },
        {
            'name': 'label_password_strength',
            'master': labelframes['labelframe_generated_password'],
            'text': 'Strength: ',
            'font': FONT_SMALL,
            'grid': {'row': 1, 'column': 0, 'pady': 10},
        },
        {
            'name': 'label_show_strength',
            'master': labelframes['labelframe_generated_password'],
            'font': FONT_BOLD,
            'grid': {'row': 1, 'column': 2},
        },
        {
            'name': 'label_entropy_calc',
            'master': labelframes['labelframe_generated_password'],
            'text': 'Total Entropy:',
            'font': FONT_SMALL,
            'grid': {'row': 2, 'column': 0, 'pady': 10},
        },
        {
            'name': 'label_entropy_value',
            'master': labelframes['labelframe_generated_password'],
            'font': FONT_BOLD,
            'grid': {'row': 2, 'column': 1, 'sticky': 'w'},
        },
        {
            'name': 'label_guidance_text',
            'master': window,
            'font': FONT_SMALL,
            'background': "#DFE4E8",
            'grid': {'row': 9, 'column': 0, 'columnspan': 3},
        },
    ]

    button_configs = [
        {
            'name': 'button_generate_password',
            'master': labelframes['labelframe_settings'],
            'text': 'Generate Password',
            'command': on_generate_password_click,
            'background': 'yellow',
            'activebackground': 'yellow',
            'anchor': 'center',
            'grid': {'row': 6, 'column': 1, 'pady': 20, 'ipady': 7, 'sticky': 'W'}
        },
        {
            'name': 'button_save',
            'master': labelframes['labelframe_buttons'],
            'text': 'Save Password',
            'command': handle_save_password,
            'grid': {'row': 0, 'column': 0, 'ipadx': 15, 'ipady': 10}
        },
        {
            'name': 'button_copy_to_clipboard',
            'master': labelframes['labelframe_buttons'],
            'text': 'Copy to clipboard',
            'command': copy_to_clipboard,
            'grid': {'row': 0, 'column': 1, 'ipadx': 15, 'ipady': 10}
        },
        {
            'name': 'button_clear',
            'master': labelframes['labelframe_buttons'],
            'text': 'Clear',
            'command': reset_password_ui,
            'grid': {'row': 0, 'column': 2, 'ipadx': 27, 'ipady': 10}
        },
        {
            'name': 'button_about',
            'master': labelframes['labelframe_buttons'],
            'text': 'About',
            'command': toggle_about_text,
            'grid': {'row': 0, 'column': 3, 'ipadx': 26, 'ipady': 10}
        },
        {
            'name': 'button_close',
            'master': labelframes['labelframe_buttons'],
            'text': 'Close',
            'command': close_app,
            'grid': {'row': 0, 'column': 4, 'ipadx': 25, 'ipady': 10}
        },
    ]

    checkbox_text = [
        'Uppercase (A, B, C, ...)',
        'Lowercase (a, b, c, ...)',
        'Digit (0, 1, 2, ...)',
        'Minus (-)',
        'Underline (_)',
        'Space ( )',
        """Symbol (!?@#$%&*^~/|\:;.,'')""",
        'Bracket ([, ], {, }, (, ), <, >)',
    ]

    checkbox_base_config = {
        'master': labelframes['labelframe_settings'],
        'font': FONT_SMALL,
        'grid': {'sticky': 'w', 'padx': 20, 'pady': 5}
    }

    checkbox_configs.clear()
    for i, text in enumerate(checkbox_text):
        option_name = re.sub(r'\s\(.*\)', '', text).lower()
        config = checkbox_base_config.copy()
        config.update({
            'text': text,
            'variable': tk.BooleanVar(value=option_name in DEFAULT_CHECKED_TYPES),
            'grid': {
                'row': 2 + i // 2,
                'column': i % 2,
                **checkbox_base_config['grid']
            }
        })
        checkbox_configs.append(config)

    style = ttk.Style(labelframes['labelframe_generated_password'])

    var = tk.StringVar()
    combobox_generated_password = ttk.Combobox(
        master=labelframes['labelframe_generated_password'],
        width=28,
        font=FONT_MEDIUM,
        values=[],
        textvariable=var,
        state='readonly',
    )
    combobox_generated_password.grid(row=0, column=1, padx=5)
    combobox_generated_password.bind("<<ComboboxSelected>>", update_password_strength_display)

    spinbox_password_length = tk.Spinbox(
        master=labelframes['labelframe_settings'],
        from_=MIN_PASSWORD_LENGTH,
        to=MAX_PASSWORD_LENGTH,
        width=20,
        relief='sunken',
    )
    spinbox_password_length.grid(row=0, column=1, pady=(30, 30), ipadx=10, ipady=5, sticky='w')

    progressbar_generated_password = ttk.Progressbar(
        master=labelframes['labelframe_generated_password'],
        style='strength.Horizontal.TProgressbar',
    )
    progressbar_generated_password.grid(row=1, column=1, padx=5, pady=10, sticky='SNEW')

    _create_widget(tk.Label, label_configs, labels)
    _create_widget(tk.Button, button_configs, buttons)
    _create_widget(tk.Checkbutton, checkbox_configs, checkboxes)

    return window



def main() -> None:
    root = build_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
