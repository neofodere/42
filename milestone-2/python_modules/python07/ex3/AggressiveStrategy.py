from __future__ import annotations
from typing import List, Dict, Any
from ex3.GameStrategy import GameStrategy


class AggressiveStrategy(GameStrategy):
    def get_strategy_name(self) -> str:
        return "AggressiveStrategy"

    def prioritize_targets(self, available_targets: List[str]) -> List[str]:
        return available_targets

    def execute_turn(
            self, hand: List[Any], battlefield: List[Any]) -> Dict[str, Any]:
        cards_played = []
        mana_used = 0
        damage = 0

        for card in hand:
            if card.cost <= 3:
                cards_played.append(card.name)
                mana_used += card.cost
                if hasattr(card, "attack"):
                    damage += card.attack
                if hasattr(
                        card, "effect_type") and card.effect_type == "damage":
                    damage += 3

        return {
            "cards_played": cards_played,
            "mana_used": mana_used,
            "targets_attacked": ["Enemy Player"],
            "damage_dealt": damage,
        }
