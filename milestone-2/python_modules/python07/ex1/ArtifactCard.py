from __future__ import annotations
from typing import Dict, Any
from ex0.Card import Card


class ArtifactCard(Card):
    def __init__(
            self, name: str, cost: int, rarity: str,
            durability: int, effect: str
    ) -> None:
        super().__init__(name, cost, rarity)
        if durability <= 0:
            raise ValueError("durability must be positive")
        self.durability = durability
        self.effect = effect

    def play(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": f"Permanent: {self.effect}",
        }

    def activate_ability(self) -> Dict[str, Any]:
        self.durability -= 1
        return {
            "artifact": self.name,
            "effect_triggered": self.effect,
            "remaining_durability": self.durability,
        }

    def get_card_info(self) -> Dict[str, Any]:
        info = super().get_card_info()
        info["type"] = "Artifact"
        info["durability"] = self.durability
        info["effect"] = self.effect
        return info
