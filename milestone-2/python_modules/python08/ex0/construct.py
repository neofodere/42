#!/usr/bin/env python3
import os
import sys
import site
from typing import Optional


def detect_virtual_env() -> Optional[str]:
    """Return the name of the virtual environment if active, else None."""
    if hasattr(sys, "base_prefix") and sys.prefix != sys.base_prefix:
        return os.path.basename(sys.prefix)
    return None


def main() -> None:
    try:
        venv_name = detect_virtual_env()
        python_path = sys.executable
        if venv_name is None:
            print("Outside the Matrix\n")
            print("MATRIX STATUS: You're still plugged in\n")
            print(f"Current Python: {python_path}")
            print("Virtual Environment: None detected\n")
            print("WARNING: You're in the global environment!")
            print("The machines can see everything you install.\n")
            print("To enter the construct, run:")
            print("python -m venv matrix_env")
            print("source matrix_env/bin/activate  # Unix")
            print("matrix_env\\Scripts\\activate   # Windows")
            print(
                  "Safe to install packages without"
                  " affecting the global system."
                  "\n"
            )
        else:
            print("Inside the Construct\n")
            print("MATRIX STATUS: Welcome to the construct\n")
            print(f"Current Python: {python_path}")
            print(f"Virtual Environment: {venv_name}")
            print(f"Environment Path: {sys.prefix}\n")
            print("SUCCESS: You're in an isolated environment!")
            print(
                  "Safe to install packages without"
                  "affecting the global system."
                  "\n"
            )
            print("Package installation path:")
            print(site.getsitepackages()[0])
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
