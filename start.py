#!/usr/bin/env python3
"""
start.py - Universal Cross-Platform Bootstrapper for CAI-TG GUI
Creates an isolated virtual environment, installs requirements, and launches the app.
"""

import os
import sys
import venv
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

REPO_FILES = [
    "start.py",
    "main.py",
    "gui.py",
    "requirements.txt",
    "README.md",
    ".gitignore"
]
RAW_BASE_URL = "https://raw.githubusercontent.com/malichevsky/cai-tg/main/"

def update_repository(root_dir):
    if "--no-update" in sys.argv:
        print("Skipping update check (--no-update).")
        return

    # Check if we are in a git repository
    if (root_dir / ".git").exists():
        print("Checking for updates via Git...")
        try:
            subprocess.check_call(["git", "pull", "--quiet"], cwd=root_dir)
            print("Successfully checked for updates via Git.")
        except subprocess.CalledProcessError as e:
             print(f"Failed to update repository: {e}")
    else:
        print("Checking for updates from GitHub...")
        for file_name in REPO_FILES:
            url = RAW_BASE_URL + file_name
            file_path = root_dir / file_name
            try:
                response = urllib.request.urlopen(url, timeout=5)
                content = response.read()
                file_path.write_bytes(content)
            except urllib.error.URLError as e:
                print(f"Failed to download {file_name}: {e}")
        print("Successfully updated files from GitHub.")

def get_venv_paths(venv_dir):
    """Return the path to the python executable and bin/Scripts directory based on OS."""
    if os.name == 'nt':  # Windows
        bin_dir = os.path.join(venv_dir, 'Scripts')
        python_exe = os.path.join(bin_dir, 'python.exe')
    else:  # Linux/Mac
        bin_dir = os.path.join(venv_dir, 'bin')
        python_exe = os.path.join(bin_dir, 'python')
    return bin_dir, python_exe

def main():
    root_dir = Path(__file__).parent.absolute()
    os.chdir(root_dir)
    
    update_repository(root_dir)
    
    venv_dir = root_dir / ".venv"
    bin_dir, python_exe = get_venv_paths(venv_dir)

    # Step 1. Create venv if it doesn't exist
    if not venv_dir.exists():
        print("Virtual environment not found. Creating .venv...")
        try:
            venv.create(venv_dir, with_pip=True)
            print("Successfully created virtual environment.")
        except BaseException as e:
            print(f"Failed to create virtual environment: {e}")
            sys.exit(1)
    
    if not os.path.exists(python_exe):
        print(f"Error: Python executable not found at expected path: {python_exe}")
        sys.exit(1)

    # Step 2. Install dependencies silently
    print("Checking and building dependencies (this may take a few seconds)...")
    try:
        subprocess.check_call(
            [python_exe, "-m", "pip", "install", "-r", "requirements.txt", "--quiet", "--upgrade"]
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

    # Step 3. Launch the GUI Application
    print("Starting CAI-TG Desktop interface...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root_dir)
    
    try:
        subprocess.run([python_exe, "gui.py"], env=env)
    except KeyboardInterrupt:
        print("\nShutdown signal received.")
    except Exception as e:
        print(f"Failed to start gui.py: {e}")

if __name__ == "__main__":
    main()
