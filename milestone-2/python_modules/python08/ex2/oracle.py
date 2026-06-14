import os
from dotenv import load_dotenv

ENV_FILE = ".env"

REQUIRED_VARS = [
    "MATRIX_MODE",
    "DATABASE_URL",
    "API_KEY",
    "LOG_LEVEL",
    "ZION_ENDPOINT",
]


def load_config() -> dict:
    """Load configuration from environment variables."""
    load_dotenv()
    return {var: os.getenv(var) for var in REQUIRED_VARS}


def validate_config(cfg: dict) -> list:
    """Return a list of missing variables."""
    missing = [key for key, value in cfg.items() if value is None]
    return missing


def check_env_file() -> str:
    """Check if .env exists and is not empty."""
    if not os.path.exists(ENV_FILE):
        return "missing"
    if os.path.getsize(ENV_FILE) == 0:
        return "empty"
    return "ok"


def main() -> None:
    print("ORACLE STATUS: Reading the Matrix...\n")
    env_status = check_env_file()
    cfg = load_config()
    missing_vars = validate_config(cfg)
    print("Configuration loaded:\n")
    for key, value in cfg.items():
        print(f"{key}: {value}")
    print("\nEnvironment security check:\n")
    if env_status == "missing":
        print("[ERROR] .env file is missing")
    elif env_status == "empty":
        print("[ERROR] .env file is empty")
    else:
        print("[OK] .env file found")
    if missing_vars:
        print("Missing variables:")
        for var in missing_vars:
            print(f" - {var}")
    else:
        print("[OK] All required variables are set")
    print("\nThe Oracle sees all configurations.")


if __name__ == "__main__":
    main()
