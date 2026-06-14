from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any


class Combatable(ABC):

    @abstractmethod
    def attack(self, target: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def defend(self, incoming_damage: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_combat_stats(self) -> Dict[str, Any]:
        pass
