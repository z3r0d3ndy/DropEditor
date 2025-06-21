from typing import List, Optional
from .models import NPC
import copy


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

    def undo(self) -> Optional[List[NPC]]:
        if self.current_index <= 0:
            return None
        self.current_index -= 1
        return copy.deepcopy(self.history[self.current_index])

    def can_undo(self) -> bool:
        return self.current_index > 0