from __future__ import annotations
from ex0.CreatureCard import CreatureCard


def main() -> None:
    print("=== DataDeck Card Foundation ===\n")
    print("Testing Abstract Base Class Design:\n")
    dragon = CreatureCard(
        name="Fire Dragon",
        cost=5,
        rarity="Legendary",
        attack=7,
        health=5,
    )
    print("CreatureCard Info:")
    print(f"{dragon.get_card_info()}\n")
    available_mana = 6
    print(f"Playing {dragon.name} with {available_mana} mana available:\n")
    print(f"Playable: {dragon.is_playable(available_mana)}")
    play_result = dragon.play(game_state={})
    print(f"Play result: {play_result}\n")
    target_name = "Goblin Warrior"
    print(f"{dragon.name} attacks {target_name}:")
    attack_result = dragon.attack_target(target_name)
    print(f"Attack result: {attack_result}\n")
    low_mana = 3
    print(f"Testing insufficient mana ({low_mana} available):")
    print(f"Playable: {dragon.is_playable(low_mana)}\n")
    print("Abstract pattern successfully demonstrated!\n")


if __name__ == "__main__":
    main()
