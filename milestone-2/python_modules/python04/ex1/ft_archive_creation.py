def main() -> None:
    """
    It tries to create a file and overwrites it if it already exists.
    """
    print("=== CYBER ARCHIVES - PRESERVATION SYSTEM ===")
    filename = "new_discovery.txt"
    print(f"Initializing new storage unit: {filename}")
    file = open(filename, "w")
    print("Storage unit created successfully...")
    print("Inscribing preservation data...")
    entries = [
        "New quantum algorithm discovered",
        "Efficiency increased by 347%",
        "Archived by Data Archivist trainee"
    ]
    entry_num = 1
    for entry in entries:
        num = str(entry_num).zfill(3)
        line = f"[ENTRY {num}] {entry}"
        print(line)
        file.write(line + "\n")
        entry_num += 1
    file.close()
    print("Data inscription complete. Storage unit sealed.")
    print(f"Archive '{filename}' ready for long-term preservation.")


if __name__ == "__main__":
    main()
