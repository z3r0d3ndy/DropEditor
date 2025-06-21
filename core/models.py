from dataclasses import dataclass
from typing import List, Optional

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