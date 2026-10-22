
<h1 align='center'> Random Password Generator - Python Tkinter </h1>

<p align='center'>
<img src="https://img.shields.io/badge/status-complete-red" />
<img src="https://img.shields.io/badge/Language-Python-03A9F4" />
<img src="https://img.shields.io/badge/Python%20Version-3.10+-blueviolet" />
<img src="https://img.shields.io/badge/Built%20With-Tkinter-brightgreen" />
<img src="https://img.shields.io/badge/Interface-GUI%20%7C%20CLI-darkblue" />
<img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux%20%7C%20Mac-795548" />
<img src="https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white" />
<img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black" />
<img src="https://img.shields.io/badge/macOS-000000?style=flat-square&logo=apple&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-yellow" />
<img src="https://img.shields.io/badge/Last%20Updated-October%202026-FF5722" />

</p>


## 📂 Table of contents

- [What is Tkinter?](#what-is-tkinter)
- [Description](#-description)
- [Installation](#-installation)
- [Requirements](#-requirements)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [License](#-license)
- [Demo](#-demo)


## What is Tkinter?

[**Tkinter**](https://docs.python.org/3/library/tkinter.html) is the standard GUI library for Python. It allows developers to create desktop applications with simple widgets like buttons, labels, entries, etc. Tkinter is built into Python, so no additional installation is required for most environments.


## 📝 Description

A Python tool to generate strong, unpredictable passwords from the command line or a desktop window. You choose the length and character types; the app generates passwords with a cryptographically secure generator and shows entropy and strength.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/shiva-rsl/random_password_generator.git
```

### 2. Navigate to the project directory

```bash
cd random_password_generator
```

### 3. Create a virtual environment

This project has been tested with Python 3.10. Using this version is recommended.

```bash
python3.10 -m venv venv
```

### 4. Activate the virtual environment

On Linux and macOS:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the command-line version

```bash
python random_password_generator_CLI.py
```

### 7. Run the GUI version

```bash
python random_password_generator_GUI.py
```

**Note for Linux users:** If creating the virtual environment fails because `ensurepip` is unavailable, install the appropriate `venv` package for Python 3.10. On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3.10-venv
```

## ⚙️ Requirements

- **Python 3.10** (recommended and tested)
- Tkinter (comes pre-installed with most Python distributions; required for the GUI)
- `colorama` (required for the CLI; installed from `requirements.txt`)

**Note:** This project has been tested with Python 3.10. Using this version is recommended for the intended GUI appearance and behavior.


## ✨ Features

This app offers the following customizable options for generating passwords:

    ✅ Lowercase letters (a, b, c, ...)

    ✅ Uppercase letters (A, B, C, ...)

    ✅ Digits (0, 1, 2, ...)

    ✅ Minus sign (-)

    ✅ Underline (_)

    ✅ Spaces ( )

    ✅ Symbols (!?@#$%&*^~/\|+=:;.,"')

    ✅ Brackets ([, ], {, }, (, ), <, >)

Additional features:

    🎯 Generate secure random passwords with `secrets` (uniform character pool)

    🔒 Define password length (8–30 characters)

    🔐 Display password entropy based on the selected character set

    🛡️ Display password strength level

    📶 Visualize password strength with a progress bar (GUI)

    📋 Copy passwords to clipboard (GUI)

    💾 Save generated passwords, with a plaintext warning (GUI)

    🗑️ Clear generated passwords (GUI)

    ❌ Exit the app easily

    ℹ️ About section for information (GUI)


## 📸 Screenshots

<img src="Screenshots/random_password_generator_main.png" width="350" height="483">


## 🧾 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

For a summary of the MIT License, see [choosealicense.com](https://choosealicense.com/licenses/mit/).


## 📽️ Demo

Coming soon...
