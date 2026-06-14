from __future__ import annotations
from ex4.TournamentCard import TournamentCard
from ex4.TournamentPlatform import TournamentPlatform


def main() -> None:
    print("=== DataDeck Tournament Platform ===\n")
    platform = TournamentPlatform()
    print("Registering Tournament Cards...\n")
    card1 = TournamentCard("Fire Dragon", 5, "Legendary", 7, 5)
    card2 = TournamentCard("Ice Wizard", 4, "Epic", 5, 6)
    id1 = platform.register_card(card1)
    id2 = platform.register_card(card2)
    print(f"{card1.name} (ID: {id1}):")
    print("- Interfaces: [Card, Combatable, Rankable]")
    print(f"- Rating: {card1.rating}")
    print(f"- Record: {card1.wins}-{card1.losses}\n")
    print(f"{card2.name} (ID: {id2}):")
    print("- Interfaces: [Card, Combatable, Rankable]")
    print(f"- Rating: {card2.rating}")
    print(f"- Record: {card2.wins}-{card2.losses}\n")
    print("Creating tournament match...\n")
    result = platform.create_match(id1, id2)
    print(f"Match result: {result}\n")
    print("Tournament Leaderboard:")
    for line in platform.get_leaderboard():
        print(line)
    print()
    print("Platform Report:")
    print(platform.generate_tournament_report())
    print("\n=== Tournament Platform Successfully Deployed! ===\n")


if __name__ == "__main__":
    main()
