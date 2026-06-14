from __future__ import annotations
from ex0.CreatureCard import CreatureCard
from ex1.SpellCard import SpellCard
from ex1.ArtifactCard import ArtifactCard
from ex1.Deck import Deck


def main() -> None:
    print("=== DataDeck Deck Builder ===\n")
    deck = Deck()
    creature = CreatureCard("Fire Dragon", 5, "Legendary", 7, 5)
    spell = SpellCard("Lightning Bolt", 3, "Rare", "damage")
    artifact = ArtifactCard("Mana Crystal", 2, "Common", 3, "+1 mana per turn")
    deck.add_card(creature)
    deck.add_card(spell)
    deck.add_card(artifact)
    print(f"Deck stats: {deck.get_deck_stats()}\n")
    deck.shuffle()
    print("Drawing and playing cards:\n")
    for _ in range(3):
        card = deck.draw_card()
        print(f"Drew: {card.name} ({card.get_card_info()['type']})")
        print(f"Play result: {card.play({})}\n")
    print(
        "Polymorphism in action: Same interface, different card behaviors!\n"
    )


if __name__ == "__main__":
    main()
