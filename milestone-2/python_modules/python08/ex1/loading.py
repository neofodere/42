import importlib
from typing import Dict, Any
REQUIRED_PACKAGES = ["pandas", "numpy", "matplotlib", "requests"]


def check_dependencies() -> Dict[str, Any]:
    """Try importing required packages and return status."""
    status = {}
    for pkg in REQUIRED_PACKAGES:
        try:
            module = importlib.import_module(pkg)
            status[pkg] = ("OK", module.__version__)
        except Exception:
            status[pkg] = ("MISSING", None)
    return status


def run_analysis() -> None:
    """Simulate data analysis and generate a plot."""
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    print("Analyzing Matrix data ...")
    data = np.random.randn(1000)
    df = pd.DataFrame({"values": data})
    print("Processing 1000 data points ...")
    plt.hist(df["values"], bins=30)
    plt.title("Matrix Data Distribution")
    plt.savefig("matrix_analysis.png")
    print("Analysis complete!")
    print("Results saved to: matrix_analysis.png")


def main() -> None:
    print("LOADING STATUS: Loading programs...\n")
    deps = check_dependencies()
    print("Checking dependencies:\n")
    missing = False
    for pkg, (state, version) in deps.items():
        if state == "OK":
            print(f"[OK] {pkg} ({version})")
        else:
            print(f"[MISSING] {pkg} - Install it using pip or Poetry")
            missing = True

    if missing:
        print("\nSome dependencies are missing.")
        print("pip install -r requirements.txt")
        print("OR")
        print("poetry install")
        return
    run_analysis()


if __name__ == "__main__":
    main()
