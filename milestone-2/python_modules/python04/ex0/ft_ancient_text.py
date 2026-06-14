def main() -> None:
    """
    Tries to open and read a file.
    """
    print("=== CYBER ARCHIVES - DATA RECOVERY SYSTEM ===")
    file = "ancient_fragment.txt"
    print(f"Accessing Storage Vault: {file}")
    try:
        file = open(file, "r")
    except FileNotFoundError:
        print("ERROR: Storage vault not found. Run data generator first.")
        return
    print("Connection established...")
    content = file.read()
    file.close()
    print("RECOVERED DATA:")
    lines = content.split("\n")
    fragment_num = 1
    for line in lines:
        if line.strip() != "":
            num = str(fragment_num).zfill(3)
            print(f"[FRAGMENT {num}] {line}")
            fragment_num += 1
    print("Data recovery complete. Storage unit disconnected.")


if __name__ == "__main__":
    main()
