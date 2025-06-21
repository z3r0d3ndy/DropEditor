from typing import List, Optional, Dict, Tuple
from .models import NPC, DropType, DropGroup, DropItem


class DropEditor:
    def __init__(self, npcs: List[NPC]):
        self.npcs = npcs

    def clear_all_drops(self, npc_types: Optional[List[str]] = None,
                        min_level: int = 0, max_level: int = 100):
        for npc in self.npcs:
            if npc_types and npc.npc_type not in npc_types:
                continue
            if not (min_level <= npc.level <= max_level):
                continue
            npc.drop_types = []

    def clear_all_except_adena(self, npc_types: Optional[List[str]] = None,
                               min_level: int = 0, max_level: int = 100):
        for npc in self.npcs:
            if npc_types and npc.npc_type not in npc_types:
                continue
            if not (min_level <= npc.level <= max_level):
                continue

            new_drop_types = []
            for drop_type in npc.drop_types:
                new_groups = []
                for group in drop_type.groups:
                    new_items = [item for item in group.items if item.id == 57]
                    if new_items:
                        group.items = new_items
                        new_groups.append(group)

                if new_groups:
                    drop_type.groups = new_groups
                    new_drop_types.append(drop_type)

            npc.drop_types = new_drop_types

    def remove_drop_type(self, npc: NPC, drop_type_name: str):
        npc.drop_types = [dt for dt in npc.drop_types if dt.name != drop_type_name]

    def remove_drop_group(self, npc: NPC, drop_type_name: str, group_name: str):
        for drop_type in npc.drop_types:
            if drop_type.name == drop_type_name:
                drop_type.groups = [g for g in drop_type.groups if g.name != group_name]
                break

    def update_drop_group(self, npc: NPC, drop_type_name: str, group_name: str,
                          new_chance: Optional[float]):
        for drop_type in npc.drop_types:
            if drop_type.name == drop_type_name:
                for group in drop_type.groups:
                    if group.name == group_name:
                        group.chance = new_chance
                        break
                break

    def update_drop_item(self, npc: NPC, drop_type_name: str, group_name: str,
                         item_id: int, new_id: int, new_min: int, new_max: int, new_chance: float):
        for drop_type in npc.drop_types:
            if drop_type.name == drop_type_name:
                for group in drop_type.groups:
                    if group.name == group_name:
                        for item in group.items:
                            if item.id == item_id:
                                item.id = new_id
                                item.min_count = new_min
                                item.max_count = new_max
                                item.chance = new_chance
                                break
                        break
                break

    def add_drop_items(self, npc_ids: List[int], levels: Tuple[int, int],
                       npc_types: List[str], drop_type: str, group_name: str,
                       group_chance: Optional[float], items: List[Dict[str, int]]):
        for npc in self.npcs:
            if npc_ids and npc.id not in npc_ids:
                continue
            if not (levels[0] <= npc.level <= levels[1]):
                continue
            if npc_types and npc.npc_type not in npc_types:
                continue

            # Find or create drop type
            dt = next((dt for dt in npc.drop_types if dt.name == drop_type), None)
            if not dt:
                dt = DropType(name=drop_type, groups=[])
                npc.drop_types.append(dt)

            # Find or create group
            group = next((g for g in dt.groups if g.name == group_name), None)
            if not group:
                group = DropGroup(name=group_name, chance=group_chance, items=[])
                dt.groups.append(group)

            # Add items
            for item_data in items:
                group.items.append(DropItem(
                    id=item_data["id"],
                    min_count=item_data["min"],
                    max_count=item_data["max"],
                    chance=item_data["chance"]
                ))