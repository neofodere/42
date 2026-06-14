from __future__ import annotations
from typing import Dict, Any
from ex3.CardFactory import CardFactory
from ex3.GameStrategy import GameStrategy


class GameEngine:
    def __init__(self) -> None:
        self.factory: CardFactory | None = None
        self.strategy: GameStrategy | None = None
        self.turns = 0
        self.total_damage = 0
        self.cards_created = 0

    def configure_engine(
            self, factory: CardFactory, strategy: GameStrategy) -> None:
        self.factory = factory
        self.strategy = strategy

    def simulate_turn(self) -> Dict[str, Any]:
        if not self.factory or not self.strategy:
            raise ValueError("Engine not configured")
        hand = [
            self.factory.create_creature("dragon"),
            self.factory.create_creature("goblin"),
            self.factory.create_spell(),
        ]
        self.cards_created += len(hand)
        result = self.strategy.execute_turn(hand, battlefield=[])
        self.turns += 1
        self.total_damage += result["damage_dealt"]
        return result

    def get_engine_status(self) -> Dict[str, Any]:
        return {
            "turns_simulated": self.turns,
            "strategy_used": self.strategy.get_strategy_name()
            if self.strategy else None,
            "total_damage": self.total_damage,
            "cards_created": self.cards_created,
        }
