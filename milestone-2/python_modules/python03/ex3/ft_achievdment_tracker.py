#!/usr/bin/env python3

def main() -> None:
    """Demonstrate achievement tracking using sets."""
    print("=== Achievement Tracker System ===")
    alice = {"first_kill", "level_10", "treasure_hunter", "speed_demon"}
    bob = {"first_kill", "level_10", "boss_slayer", "collector"}
    charlie = {
        "level_10",
        "treasure_hunter",
        "boss_slayer",
        "speed_demon",
        "perfectionist",
    }
    print(f"Player alice achievements: {alice}")
    print(f"Player bob achievements: {bob}")
    print(f"Player charlie achievements: {charlie}")
    print("=== Achievement Analytics ===")
    all_unique = alice.union(bob).union(charlie)
    print(f"All unique achievements: {all_unique}")
    print(f"Total unique achievements: {len(all_unique)}")
    common_all = alice.intersection(bob).intersection(charlie)
    print(f"Common to all players: {common_all}")
    rare = (
        (alice.difference(bob).difference(charlie)) |
        (bob.difference(alice).difference(charlie)) |
        (charlie.difference(alice).difference(bob))
    )
    print(f"Rare achievements (1 player): {rare}")
    alice_bob_common = alice.intersection(bob)
    print(f"Alice vs Bob common: {alice_bob_common}")
    alice_unique = alice.difference(bob)
    print(f"Alice unique: {alice_unique}")
    bob_unique = bob.difference(alice)
    print(f"Bob unique: {bob_unique}")


if __name__ == "__main__":
    main()
