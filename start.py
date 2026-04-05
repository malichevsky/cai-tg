#!/usr/bin/env python3
"""
start.py - Universal Cross-Platform Bootstrapper for CAI-TG GUI
Creates an isolated virtual environment, installs requirements, and launches the app.
"""

import os
import sys
import venv
import subprocess
from pathlib import Path

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
    
    venv_dir = root_dir / ".venv"
    bin_dir, python_exe = get_venv_paths(venv_dir)

    # Step 1. Create venv if it doesn't exist or is broken
    if not venv_dir.exists() or not os.path.exists(python_exe):
        if venv_dir.exists():
            print("Virtual environment appears broken. Recreating .venv...")
            import shutil
            shutil.rmtree(venv_dir, ignore_errors=True)

        print("Creating virtual environment...")
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
