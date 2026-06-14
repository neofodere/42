from __future__ import annotations
from typing import Dict, Any, List
from ex0.Card import Card
from ex2.Combatable import Combatable
from ex2.Magical import Magical


class EliteCard(Card, Combatable, Magical):
    def __init__(
        self,
        name: str,
        cost: int,
        rarity: str,
        attack: int,
        defense: int,
        mana: int,
    ) -> None:
        super().__init__(name, cost, rarity)
        self.attack_power = attack
        self.defense_power = defense
        self.mana = mana

    def play(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": "Elite card deployed with combat and magic abilities",
        }

    def attack(self, target: str) -> Dict[str, Any]:
        return {
            "attacker": self.name,
            "target": target,
            "damage": self.attack_power,
            "combat_type": "melee",
        }

    def defend(self, incoming_damage: int) -> Dict[str, Any]:
        blocked = min(self.defense_power, incoming_damage)
        taken = incoming_damage - blocked
        alive = taken < 10
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

    def cast_spell(
            self, spell_name: str, targets: List[str]) -> Dict[str, Any]:
        mana_used = min(self.mana, 4)
        self.mana -= mana_used
        return {
            "caster": self.name,
            "spell": spell_name,
            "targets": targets,
            "mana_used": mana_used,
        }

    def channel_mana(self, amount: int) -> Dict[str, Any]:
        self.mana += amount
        return {
            "channeled": amount,
            "total_mana": self.mana,
        }

    def get_magic_stats(self) -> Dict[str, Any]:
        return {
            "mana": self.mana,
        }
