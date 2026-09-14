import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile
from typing import Type, Dict, List, Any
from utils import *

# ----------------------------- Constants ----------------------------- 

# Fonts
FONT_LARGE = ('Noto Sans', 20)
FONT_MEDIUM = ('Noto Sans', 15)
FONT_NORMAL = ('Noto Sans', 12)
FONT_SMALL = ('Noto Sans', 10)
FONT_BOLD = ('Noto Sans', 12, 'bold')

# Colors
SOFTWARE_COLOR_BACKGROUND = '#DFE4E8'
COLOR_BACKGROUND = "#000000"
COLOR_FORGROUND = "#F0CF28"

ABOUT_TEXT = '''The Random Password Generator enables you to generate secure and highly
    unpredictable passwords through an optional mix of lowercase and uppercase letters,
    numbers and special characters.'''


# ----------------------------- Global Variables ----------------------------- 
checkbox_variables = []
checkbox_configs = []
password_list = []
password_option = {}
labelframes = {}
checkboxes = {}
buttons = {}
labels = {}


# ----------------------------- Utility Functions ----------------------------- #

clear_screen()


def show_checkbox_error_message() -> None:
    """
    shows an error popup if user has not checked any checkboxes.
    """
    messagebox.showinfo('Error', 'Please check at lease one checkbox to proceed.')


def show_invalid_password_length_message() -> None:
    """
    Displays an error popup if the password length is not valid.
    """
    messagebox.showinfo(
        'Error', 
        f'Password length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters.'
    )


def get_spinbox_password_length() -> int | None:
    """
    Retrieve the password length form the spinbox.

    Returns:
        int: The selected password length.
    """
    return int(spinbox_password_length.get())


def set_password_length() -> None:
    """
    Sets the password length in the `password_option` dictionary if valid.
    Raises a ValueError if is invalid.

    Side Effects:
        Updates global `password_option` if valid.

    Raises:
        ValueError: If the password length is invalid (e.g., below minimum or above maximum allowed).

    Returns:
        None
    """
    password_length = get_spinbox_password_length()
    if not is_valid_password_length(password_length):
        raise ValueError
    password_option['password_length'] = password_length


def get_selected_password() -> str:
    """Fetch the latest selected password from the combobox."""
    return combobox_generated_password.get()


def show_password_entropy(*args) -> None:
    """
    Calculates and displays the password entropy in the GUI label.

    Side Effects:
        - Calls `calculate_password_entropy()` to compute the entropy
        - Formats the result to 2 decimal places
        - Updates the text of `label_entropy_value` with the result

    Returns:
        None
    """
    selected_password = get_selected_password()
    password_entropy_value = calculate_password_entropy(selected_password)
    labels['label_entropy_value'].config(text=f'{password_entropy_value:.2f} bits')


def update_password_strength_label() -> None:
    """
    Updates the password strength rating and its associated color in the GUI.

    Side Effects:
    1. Retrieves the strength level and color by calling `calculate_password_strength()`
    2. Updates the `label_show_strength` widget with:
       - Text: The strength level (e.g., "🔴 Very Weak")
       - Foreground color: The associated color code (e.g., "#f01010")

    Returns:
        None
    """
    selected_password = get_selected_password()
    _, strength_level, strength_color  = calculate_password_strength(selected_password)
    labels['label_show_strength'].config(text=strength_level, fg=strength_color)


def get_password_options_from_user() -> None:
    """
    Updates the global `password_option` dictionary based on the current user-selected checkbox values.

    Side Effects:
        - Modifies the global `password_option` dictionary by extracting checkbox states from `checkbox_configs`.
    
    Returns:
        None
    """
    for config in checkbox_configs:
        text = config['text']
        checkbox_name = re.sub(r'\s\(.*\)', '', text)
        variable_value = config['variable'].get()
        password_option[checkbox_name.lower()] = variable_value


def generate_password() -> str:
    """
    Generates a random password based on the options selected by the user.

    Side Effects:
        - Calls the `random_password_generator()` to generate password.
        - Appends the generated password to the global `password_list`.

    Returns:
        str: The newely generated password.
    """
    generated_password = random_password_generator(password_option)
    password_list.append(generated_password)
    return generated_password


def show_generated_password_in_combobox() -> None:
    """
    Displays the list of generated passwords in the combobox widget.
    
    Side Effects:
        - Updates the values of `combobox_generated_password` with the current `password_list`.
        - Sets the combobox selection to the most recently generated password.

    Returns:
        None
    """
    combobox_generated_password.config(values=password_list)
    combobox_generated_password.set(password_list[-1])


def show_password_strength_in_progressbar() -> None:
    """
    Updates the password strength progress bar's value and color based on password entropy.
    
    Side Effects:
        - Calls `calculate_password_entropy()` to compute the entropy of the current password.
        - Updates the progress bar value and color to visually reflect password strength.
        
    Returns:
        None
    """
    selected_password = get_selected_password()
    strength, _, color = calculate_password_strength(selected_password)
    style.configure('strength.Horizontal.TProgressbar', background=color)
    progressbar_generated_password.config(value=strength)


def update_password_strength_display(*args) -> None:
    """
    Updates the entire password strength view, including:
        - Entropy display
        - Strength label
        - Progress bar
    """
    show_password_entropy()
    update_password_strength_label()
    show_password_strength_in_progressbar()


def on_generate_password_click() -> None:
    """
    Handles the event triggered by the 'Generate Password' button.

    Steps performed:
        1. Retrives and validates the user_specified password length.
        2. Updates `password_option` based on user selections.
        3. Generates a password using the specified options.
        4. Displays the generated password in the combobox.
        5. Shows the password entropy.
        6. Shows the textual strength indicator.
        7. Updates the progress bar based on password strength.
    
    Handles:
        - IndexError by showing a checkbox selection error message.

    Returns:
        None
    """

    try:

        set_password_length()

        get_password_options_from_user()

        generate_password()
        
        show_generated_password_in_combobox()

        update_password_strength_display()

    except IndexError:
        show_checkbox_error_message()
    
    except ValueError:
        show_invalid_password_length_message()


def save_password_to_file() -> None:
    """
    Prompts the user with a file save dialog and writes the given password.
    
    Args:
        password (str): The password to save.

    Side Effects:
        - Opens a file dialog to select the save location.
        - Writes the password content to the selected file.

    Returns:
        None
    """

    file = asksaveasfile(
            mode='w', 
            title='Save Passwords', 
            filetypes=[('Text Document','*.txt'), ('All Files', '*.*')], 
            defaultextension='.txt', 
        )

    if file:
        try:
            file.write("\n".join(password_list))
        finally:
            file.close()


def show_save_error_if_empty(password: str) -> bool:
    """
    Validates if a password is available for saving.
    
    Args:
        password (str): The password to validate.

    Side Effects:
        Shows a messagebox if the password is empty.

    Returns:
        bool: True if a password exists, False otherwise.
    """
    if not password:
        messagebox.showinfo('Error', 'There is nothing to be saved!')
        return False
    return True


def handle_save_password() -> None:
    """
    Validates and saves the generated password to a user-specified file.
    
    Side Effects:
        Shows error popup if no password is availabel.
        Opens a file dialog for saving the password.

    Return:
        None
    """
    generated_password = var.get()
    if show_save_error_if_empty(generated_password):
        save_password_to_file()
    

def show_copy_error_if_empty(generated_password: str) -> bool:
    """
    Checks if the generated password is empty. if so, shows an error messagebox.
    
    Args:
        `generated_password` (str): The password string to check.

    Side Effects:
        Displays a messagebox if the password is empty.

    Returns:
        bool: True if an error was shown, False otherwise.
    """
    if not generated_password:
        messagebox.showinfo('Error', 'There is nothing to be copied!')
        return True
    return False


def show_copy_message() -> None:
    """
    Displays a confirmation message 'Password copied!' in `label_guidance_text`,
    then clears the message after 2 seconds.

    Side Effects:
        - Modifies the label text of `label_guidance_text`.
        - Uses `after()` to clear it after 2 seconds.

    Returns:
        None
    """
    labels['label_guidance_text'].config(
        text='Password copied!', 
        fg="#066A10"
    )
    window.after(2000, lambda: labels['label_guidance_text'].config(text=''))


def copy_to_clipboard() -> None:
    """
    Copies the generated password to clipboard.
    Shows an error if password is empty.

    Side Effects:
        - Displays an error popup if the password is empty.
        - Copies the password to the system clipboard.
        - Updates the `label_guidance_text` to show a confirmation message.

    Returns:
        None
    """
    generated_password = var.get()

    if show_copy_error_if_empty(generated_password):
        return
    
    labelframes['labelframe_generated_password'].clipboard_clear()
    labelframes['labelframe_generated_password'].clipboard_append(generated_password)
    
    show_copy_message()


def reset_password_ui() -> None:
    """
    Resets all password-related GUI elements to their default empty state.

    Side Effects:
        - Clears the global `password_list`
        - Resets the password combobox (current selection and dropdown values)
        - Clears the entropy value display
        - Resets the strength indicator text
        - Sets the progress bar to 0

    Returns:
        None
    """
    global password_list
    password_list.clear()
    combobox_generated_password.set('')
    combobox_generated_password.config(values=())
    labels['label_entropy_value'].config(text='')
    labels['label_show_strength'].config(text='')
    progressbar_generated_password.config(value=0)


def toggle_about_text() -> None:
    """
    Displays or toggles the application description in the `label_guidance_text`.

    Side Effects:
        - Shows `ABOUT_TEXT` in black if the label is empty
        - Clears the Label if it already contains text
    """
    if not labels['label_guidance_text']['text'].strip():
        labels['label_guidance_text'].config(text=ABOUT_TEXT, fg=COLOR_BACKGROUND)
    else:
        labels['label_guidance_text'].config(text='')


def close_app() -> None:
    """
    Displays a confirmation dialog and closes the application if user confirms.
    """
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()


def _create_widget(
    widget_type: Type[tk.Widget],
    widget_config_list: List[Dict[str, Any]],
    widget_collection: Dict[str, tk.Widget]
) -> None:
    """
    Creates and places tkinter widgets based on a list of configurations.

    Args:
        widget_type: The tkinter widget class (e.g., tk.Label, tk.Button, tk.Checkbutton)
        widget_config_list (list[dict]): List of widget configuration dictionaries.
        widget_collection (dict): Dictionary to store created widgets, keyed by their 'name'
                                   (or auto-generated if missing).

    Side Effects:
        Adds widgets to the GUI and stores them in widget_collection.
    """
    for i, config in enumerate(widget_config_list):
        widget = widget_type(
            master=config['master'],
            font=config.get('font'),
            text=config.get('text'),
            background=config.get('background'),
            foreground=config.get('foreground'),
            activebackground=config.get('activebackground'),
            anchor=config.get('anchor'),
            command=config.get('command'),
            variable=config.get('variable'),     
            value=config.get('value'),           
        )

        widget.grid(**config['grid'])

        widget_name = config.get('name', f"{widget_type.__name__.lower()}_{i}")
        widget_collection[widget_name] = widget


# ----------------------------- GUI Initialization ----------------------------- #

window = tk.Tk()
window.title('Random Password Generator App')
window.config(bg=SOFTWARE_COLOR_BACKGROUND)
window.geometry('700x840')
window.resizable(width=False, height=False)


window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=2)
window.columnconfigure(2, weight=1)



# LabelFrames
labelframe_configs = [
    {
        'name': 'labelframe_settings',
        'master': window, 
        'text': 'Password settings', 
        'font': FONT_LARGE, 
        'grid': {'row':2, 'column':0, 'columnspan':5, 'padx':(10, 10), 'pady':(10, 0), 'sticky':'EW'}
    },
    {
        'name': 'labelframe_generated_password',
        'master': window,
        'text': 'Generated Password(s)',
        'font': FONT_LARGE,
        'grid': {'row':3, 'column':0, 'ipadx':120, 'ipady':5, 'padx':(10, 10), 'pady':(10, 10)}
    },
    {
        'name': 'labelframe_buttons',
        'master': window,
        'grid': {'row':4, 'column':0, 'ipadx':15, 'ipady':0, 'padx':(10, 10), 'pady':(5, 10)}
    },
]


_create_widget(tk.LabelFrame, labelframe_configs, labelframes)


for col in range(3):
    labelframes['labelframe_settings'].columnconfigure(col, weight=1)


# Labels
label_configs = [
    {
        'name': 'label_title',
        'master': window,
        'text': 'Random Password Generator',
        'font': FONT_LARGE,
        'background': COLOR_BACKGROUND,
        'foreground': COLOR_FORGROUND,
        'grid': {'row':0, 'column':0, 'columnspan':5, 'ipadx':250, 'ipady':15, 'sticky':'NSEW'},
    },
    {
        'name': 'label_subtitle',
        'master': window,
        'text': 'A free tool to quickly create your password',
        'font': FONT_NORMAL,
        'background': COLOR_BACKGROUND,
        'foreground': COLOR_FORGROUND,
        'grid': {'row':1, 'column':0, 'columnspan':5, 'ipady':5, 'sticky':'NEW',},
    },
    {
        'name': 'label_password_length',
        'master': labelframes['labelframe_settings'],
        'text': 'Length of generated password: ',
        'font': FONT_SMALL,
        'grid': {'row':0, 'column':0, 'padx':(30, 0), 'pady':(30, 30), 'sticky':'w'},
    },
    {
        'name': 'label_password_length_numbers',
        'master': labelframes['labelframe_settings'],
        'text': '(8 to 30 Chars)',
        'font': FONT_SMALL,
        'grid': {'row':0, 'column':2, 'padx':(0, 80), 'pady':(30, 30), 'sticky':'w'},
    },
    {
        'name': 'label_random_password',
        'master': labelframes['labelframe_generated_password'],
        'text': 'Password: ',
        'font': FONT_MEDIUM,
        'grid': {'row':0, 'column':0, 'padx':20, 'pady':30, 'sticky':'E'},
    },
    {
        'name': 'label_password_strength',
        'master': labelframes['labelframe_generated_password'],
        'text': 'Strength: ',
        'font': FONT_SMALL,
        'grid': {'row':1, 'column':0, 'pady':10},
    },
    {
        'name': 'label_show_strength',
        'master': labelframes['labelframe_generated_password'],
        'font': FONT_BOLD,
        'grid': {'row':1, 'column':2,},

    },
    {
        'name': 'label_entropy_calc',
        'master': labelframes['labelframe_generated_password'],
        'text': 'Total Entropy:',
        'font': FONT_SMALL,
        'grid': {'row':2, 'column':0, 'pady':10},
    },
    {
        'name': 'label_entropy_value',
        'master': labelframes['labelframe_generated_password'],
        'font': FONT_BOLD,
        'grid': {'row':2, 'column':1, 'sticky':'w'},
    },
    {
        'name': 'label_guidance_text',
        'master': window,
        'font': FONT_SMALL,
        'background': "#DFE4E8",
        'grid': {'row':9, 'column':0, 'columnspan':3,},
    },
]


# Buttons
button_configs = [
    {
        'name': 'button_generate_password',
        'master': labelframes['labelframe_settings'],
        'text': 'Generate Password',
        'command': on_generate_password_click,
        'background': 'yellow', 
        'activebackground': 'yellow',
        'anchor': 'center',
        'grid': {'row':6, 'column':1, 'pady':20, 'ipady':7, 'sticky':'W'}
    },
    {
        'name': 'button_save',
        'master': labelframes['labelframe_buttons'],
        'text': 'Save Password',
        'command': handle_save_password,
        'grid': {'row':0, 'column':0, 'ipadx':15, 'ipady':10}
    },
    {
        'name': 'button_copy_to_clipboard',
        'master': labelframes['labelframe_buttons'],
        'text': 'Copy to clipboard',
        'command': copy_to_clipboard,
        'grid': {'row':0, 'column':1, 'ipadx':15, 'ipady':10}
    },
    {
        'name': 'button_clear',
        'master': labelframes['labelframe_buttons'],
        'text': 'Clear',
        'command': reset_password_ui,
        'grid': {'row':0, 'column':2, 'ipadx':27, 'ipady':10}
    },
    {
        'name': 'button_about',
        'master': labelframes['labelframe_buttons'],
        'text': 'About',
        'command': toggle_about_text,
        'grid': {'row':0, 'column':3, 'ipadx':26, 'ipady':10}
    },
    {
        'name': 'button_close',
        'master': labelframes['labelframe_buttons'],
        'text': 'Close',
        'command': close_app,
        'grid': {'row':0, 'column':4, 'ipadx':25, 'ipady':10}
    },
]


# Checkboxs
checkbox_text = [
    'Uppercase (A, B, C, ...)',
    'Lowercase (a, b, c, ...)',
    'Digit (0, 1, 2, ...)',
    'Minus (-)',
    'Underline (_)',
    'Space ( )',
    """Symbol (!?@#$%&*^~/|\:;.,\'\')""",
    'Bracket ([, ], {, }, (, ), <, >)',
]


checkbox_base_config = {
    'master': labelframes['labelframe_settings'],
    'font': FONT_SMALL,
    'variable': tk.BooleanVar,
    'grid': {'sticky': 'w', 'padx': 20, 'pady': 5}
}


for i, text in enumerate(checkbox_text):
    
    config = checkbox_base_config.copy()
    config.update({
        'text': text,
        'variable': checkbox_base_config['variable'](),
        'grid': {
            'row': 2 + i // 2,
            'column': i % 2,
            **checkbox_base_config['grid']
        }
    })
    checkbox_configs.append(config)


# Style
style = ttk.Style(labelframes['labelframe_generated_password'])


# Combobox
var = tk.StringVar()
combobox_generated_password = ttk.Combobox(
    master=labelframes['labelframe_generated_password'],
    width=28,
    font=FONT_MEDIUM,
    values=password_list,
    textvariable=var,
)
combobox_generated_password.grid(row=0, column=1, padx=5)
combobox_generated_password.bind("<<ComboboxSelected>>", update_password_strength_display)


# Spinbox
spinbox_password_length = tk.Spinbox(
    master=labelframes['labelframe_settings'], 
    from_=8, 
    to=30, 
    width=20,
    relief='sunken',
)
spinbox_password_length.grid(row=0, column=1, pady=(30, 30), ipadx=10, ipady=5, sticky='w')


# ProgressBar
progress_var = tk.DoubleVar()
progressbar_generated_password = ttk.Progressbar(
    master=labelframes['labelframe_generated_password'],
    style='strength.Horizontal.TProgressbar',
)
progressbar_generated_password.grid(row=1, column=1, padx=5, pady=10, sticky='SNEW') 


_create_widget(tk.Label, label_configs, labels)
_create_widget(tk.Button, button_configs, buttons)
_create_widget(tk.Checkbutton, checkbox_configs, checkboxes)


window.mainloop()
