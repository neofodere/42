def crisis_handler(filename: str) -> None:
    print(f"CRISIS ALERT: Attempting access to '{filename}'...")
    try:
        with open(filename, "r") as f:
            content = f.read()
            print(f"SUCCESS: Archive recovered - ``{content.strip()}``")
            print("STATUS: Normal operations resumed")
            return
    except FileNotFoundError:
        print("RESPONSE: Archive not found in storage matrix")
        print("STATUS: Crisis handled, system stable")
    except PermissionError:
        print("RESPONSE: Security protocols deny access")
        print("STATUS: Crisis handled, security maintained")
    except Exception:
        print("RESPONSE: Unexpected system anomaly detected")
        print("STATUS: Crisis contained with emergency protocols")


def main() -> None:
    print("=== CYBER ARCHIVES - CRISIS RESPONSE SYSTEM ===")
    crisis_handler("lost_archive.txt")
    crisis_handler("classified_vault.txt")
    crisis_handler("standard_archive.txt")
    print("All crisis scenarios handled successfully. Archives secure.")
