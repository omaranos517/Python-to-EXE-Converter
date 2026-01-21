<p align="right">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="50" height="50"/>
</p>

# Python to EXE Converter
A simple and user-friendly GUI application to convert Python scripts (`.py` / `.pyw`) into standalone executable files (`.exe`) using **PyInstaller**.

## Features

- Select a Python file to convert.
- Choose a custom output folder.
- Add a custom icon (`.ico`) to your executable.
- Hide the console window for GUI applications (optional).
- Build as a **single executable file** (`onefile`) or **directory with dependencies** (`onedir`).
- Loading spinner with dynamic messages to indicate progress.

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/omaranos517/Python-to-EXE-Converter.git
cd python-to-exe
```
2. Install dependencies:
```bash
pip install pyinstaller
```
3. Run the application:
```bash
python build.py
```

## How to Use
1. **Select Script:** Click the "Browse" button to find your `.py` file.
2. **Settings:** Toggle "One File" if you want a single executable.
3. **Icon (Optional):** Select a `.ico` file to brand your app.
4. **Convert:** Hit the convert button and wait for the "Success" message!
