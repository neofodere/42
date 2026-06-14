from __future__ import annotations
from typing import Dict, List
import random
from ex4.TournamentCard import TournamentCard


class TournamentPlatform:
    def __init__(self) -> None:
        self.cards: Dict[str, TournamentCard] = {}
        self.matches_played = 0

    def register_card(self, card: TournamentCard) -> str:
        card_id = (
            f"{card.name.lower().replace(' ', '_')}_"
            f"{len(self.cards) + 1:03d}"
        )
        self.cards[card_id] = card
        return card_id

    def create_match(self, card1_id: str, card2_id: str) -> Dict:
        if card1_id not in self.cards or card2_id not in self.cards:
            raise ValueError("Invalid card IDs")
        card1 = self.cards[card1_id]
        card2 = self.cards[card2_id]
        score1 = card1.attack_power + random.randint(0, 5)
        score2 = card2.attack_power + random.randint(0, 5)
        if score1 > score2:
            winner, loser = card1_id, card2_id
        elif score2 > score1:
            winner, loser = card2_id, card1_id
        else:
            winner, loser = random.choice([
                (card1_id, card2_id), (card2_id, card1_id)])
        self.cards[winner].update_wins(1)
        self.cards[loser].update_losses(1)
        self.matches_played += 1
        return {
            "winner": winner,
            "loser": loser,
            "winner_rating": self.cards[winner].rating,
            "loser_rating": self.cards[loser].rating,
        }

    def get_leaderboard(self) -> List[str]:
        sorted_cards = sorted(
            self.cards.items(),
            key=lambda x: x[1].rating,
            reverse=True,
        )
        return [
            f"{i + 1}. {card.name} - Rating: {card.rating} "
            f"({card.wins}-{card.losses})"
            for i, (_, card) in enumerate(sorted_cards)
        ]

    def generate_tournament_report(self) -> Dict[str, int | float | str]:
        if not self.cards:
            avg_rating = 0
        else:
            avg_rating = sum(c.rating for c in self.cards.values()
                             ) / len(self.cards)
        return {
            "total_cards": len(self.cards),
            "matches_played": self.matches_played,
            "avg_rating": int(avg_rating),
            "platform_status": "active" if self.matches_played > 0 else "idle",
        }
