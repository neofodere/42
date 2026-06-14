from __future__ import annotations
from ex2.EliteCard import EliteCard


def main() -> None:
    print("=== DataDeck Ability System ===\n")
    elite = EliteCard(
        name="Arcane Warrior",
        cost=4,
        rarity="Epic",
        attack=5,
        defense=3,
        mana=4,
    )
    print("EliteCard capabilities:\n")
    print("- Card: ['play', 'get_card_info', 'is_playable']\n")
    print("- Combatable: ['attack', 'defend', 'get_combat_stats']\n")
    print("- Magical: ['cast_spell', 'channel_mana', 'get_magic_stats']\n")
    print("Playing Arcane Warrior (Elite Card):\n")
    print(f"{elite.play({})}\n")
    print("Combat phase:\n")
    print(f"Attack result: {elite.attack('Enemy')}\n")
    print(f"Defense result: {elite.defend(5)}\n")
    print("Magic phase:\n")
    print(
        f"Spell cast: {elite.cast_spell('Fireball', ['Enemy1', 'Enemy2'])}\n"
    )
    print(f"Mana channel: {elite.channel_mana(3)}\n")
    print("Multiple interface implementation successful!\n")


if __name__ == "__main__":
    main()
