from __future__ import annotations
from typing import Dict, Any
from ex0.Card import Card
from ex2.Combatable import Combatable
from ex4.Rankable import Rankable


class TournamentCard(Card, Combatable, Rankable):
    def __init__(
        self,
        name: str,
        cost: int,
        rarity: str,
        attack: int,
        defense: int,
    ) -> None:
        super().__init__(name, cost, rarity)
        self.attack_power = attack
        self.defense_power = defense
        self.wins = 0
        self.losses = 0
        self.rating = 1200

    def play(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": "Tournament card deployed",
        }

    def attack(self, target: str) -> Dict[str, Any]:
        return {
            "attacker": self.name,
            "target": target,
            "damage": self.attack_power,
            "combat_type": "tournament_melee",
        }

    def defend(self, incoming_damage: int) -> Dict[str, Any]:
        blocked = min(self.defense_power, incoming_damage)
        taken = incoming_damage - blocked
        alive = taken < 15
        return {
            "defender": self.name,
            "damage_taken": taken,
            "damage_blocked": blocked,
            "still_alive": alive,
        }

    def get_combat_stats(self) -> Dict[str, Any]:
        return {
            "attack": self.attack_power,
            "defense": self.defense_power,
        }

    def calculate_rating(self) -> int:
        return 1200 + (self.wins * 16) - (self.losses * 16)

    def update_wins(self, wins: int) -> None:
        self.wins += wins
        self.rating = self.calculate_rating()

    def update_losses(self, losses: int) -> None:
        self.losses += losses
        self.rating = self.calculate_rating()

    def get_rank_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rating": self.rating,
            "wins": self.wins,
            "losses": self.losses,
        }

    def get_tournament_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rating": self.rating,
            "record": f"{self.wins}-{self.losses}",
            "combat_stats": self.get_combat_stats(),
        }
