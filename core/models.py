from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import copy


@dataclass
class DropItem:
    id: int
    min_count: int
    max_count: int
    chance: float


@dataclass
class DropGroup:
    name: str
    chance: Optional[float]
    items: List[DropItem]


@dataclass
class DropType:
    name: str
    groups: List[DropGroup]


@dataclass
class NPC:
    id: int
    name: str
    level: int
    npc_type: str
    drop_types: List[DropType]


class History:
    def __init__(self, max_steps=5):
        self.max_steps = max_steps
        self.history = []
        self.current_index = -1

    def add_state(self, npcs: List[NPC]):
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]

        serialized = [copy.deepcopy(npc) for npc in npcs]
        self.history.append(serialized)

        if len(self.history) > self.max_steps:
            self.history.pop(0)
        else:
            self.current_index = len(self.history) - 1

    def undo(self, current_npcs: List[NPC]) -> Optional[List[NPC]]:
        if self.current_index <= 0:
            return None

        self.current_index -= 1
        return copy.deepcopy(self.history[self.current_index])

    def redo(self, current_npcs: List[NPC]) -> Optional[List[NPC]]:
        if self.current_index >= len(self.history) - 1:
            return None

        self.current_index += 1
        return copy.deepcopy(self.history[self.current_index])