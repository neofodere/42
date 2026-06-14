from __future__ import annotations
from typing import Dict, Any
import random
from ex3.CardFactory import CardFactory
from ex0.CreatureCard import CreatureCard
from ex1.SpellCard import SpellCard
from ex1.ArtifactCard import ArtifactCard


class FantasyCardFactory(CardFactory):
    def create_creature(self, name_or_power=None) -> CreatureCard:
        if name_or_power == "dragon":
            return CreatureCard("Fire Dragon", 5, "Legendary", 7, 5)
        if name_or_power == "goblin":
            return CreatureCard("Goblin Warrior", 2, "Common", 2, 1)
        return CreatureCard("Wolf", 3, "Common", 3, 2)

    def create_spell(self, name_or_power=None) -> SpellCard:
        return SpellCard("Lightning Bolt", 3, "Rare", "damage")

    def create_artifact(self, name_or_power=None) -> ArtifactCard:
        return ArtifactCard("Mana Ring", 2, "Uncommon", 3, "+1 mana per turn")

    def create_themed_deck(self, size: int) -> Dict[str, Any]:
        deck = []
        for _ in range(size):
            choice = random.choice(["creature", "spell", "artifact"])
            if choice == "creature":
                deck.append(self.create_creature("goblin"))
            elif choice == "spell":
                deck.append(self.create_spell())
            else:
                deck.append(self.create_artifact())
        return {"cards": deck}

    def get_supported_types(self) -> Dict[str, Any]:
        return {
            "creatures": ["dragon", "goblin"],
            "spells": ["fireball"],
            "artifacts": ["mana_ring"],
        }
