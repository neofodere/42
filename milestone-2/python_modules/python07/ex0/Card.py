from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict


class Card(ABC):
    def __init__(self, name: str, cost: int, rarity: str) -> None:
        if cost < 0:
            raise ValueError("cost must be non-negative")
        self.name = name
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def play(self, game_state: Dict) -> Dict:
        """
        Execute the card's effect and return a game_state-like dict.
        """
        raise NotImplementedError

    def get_card_info(self) -> Dict:
        """
        Return basic information about the card.
        """
        return {
            "name": self.name,
            "cost": self.cost,
            "rarity": self.rarity,
            "type": self.__class__.__name__.replace("Card", "") or "Card",
        }

    def is_playable(self, available_mana: int) -> bool:
        """
        Check if the card can be played with the given available mana.
        """
        return available_mana >= self.cost
