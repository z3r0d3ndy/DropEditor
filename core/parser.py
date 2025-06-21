from lxml import etree
from pathlib import Path
from typing import List, Optional, Tuple
from .models import NPC, DropType, DropGroup, DropItem


def parse_npc(xml_path: Path) -> List[NPC]:
    try:
        tree = etree.parse(xml_path)
        npcs = []

        for npc_elem in tree.xpath("//npc"):
            try:
                npc_id = int(npc_elem.get("id"))
                name = npc_elem.get("name", "Unknown")
                level = 0
                npc_type = "Monster"

                for set_elem in npc_elem.xpath(".//set"):
                    if set_elem.get("name") == "level":
                        level = int(set_elem.get("value", 0))
                    elif set_elem.get("name") == "type":
                        npc_type = set_elem.get("value", "Monster")

                drop_types = []
                for rewardlist in npc_elem.xpath(".//rewardlist"):
                    drop_type = rewardlist.get("type")
                    if not drop_type:
                        continue

                    groups = []
                    for group_elem in rewardlist.xpath(".//group"):
                        group_name = group_elem.get("name", "")
                        group_chance = float(group_elem.get("chance")) if group_elem.get("chance") else None

                        items = []
                        for reward in group_elem.xpath(".//reward"):
                            items.append(DropItem(
                                id=int(reward.get("item_id")),
                                min_count=int(reward.get("min", 1)),
                                max_count=int(reward.get("max", 1)),
                                chance=float(reward.get("chance", 0))
                            ))

                        if items:
                            groups.append(DropGroup(
                                name=group_name,
                                chance=group_chance,
                                items=items
                            ))

                    direct_items = []
                    for reward in rewardlist.xpath(".//reward[not(parent::group)]"):
                        direct_items.append(DropItem(
                            id=int(reward.get("item_id")),
                            min_count=int(reward.get("min", 1)),
                            max_count=int(reward.get("max", 1)),
                            chance=float(reward.get("chance", 0))
                        ))

                    if direct_items:
                        groups.append(DropGroup(
                            name="Direct Drops",
                            chance=None,
                            items=direct_items
                        ))

                    if groups:
                        drop_types.append(DropType(
                            name=drop_type,
                            groups=groups
                        ))

                npcs.append(NPC(
                    id=npc_id,
                    name=name,
                    level=level,
                    npc_type=npc_type,
                    drop_types=drop_types
                ))
            except Exception as e:
                print(f"Error parsing NPC: {e}")
                continue

        return npcs
    except Exception as e:
        print(f"Error parsing file {xml_path}: {e}")
        return []


def load_npcs_from_folder(folder_path: Path) -> List[NPC]:
    return [npc for xml_file in folder_path.rglob("*.xml") for npc in parse_npc(xml_file)]


def get_unique_npc_types(npcs: List[NPC]) -> List[str]:
    return sorted(list({npc.npc_type for npc in npcs if npc.npc_type}))


def save_npcs_to_folder(npcs: List[NPC], folder_path: Path):
    for npc in npcs:
        file_path = folder_path / f"{npc.id}.xml"

        root = etree.Element("npc", id=str(npc.id), name=npc.name)
        etree.SubElement(root, "set", name="level", value=str(npc.level))
        etree.SubElement(root, "set", name="type", value=npc.npc_type)

        drops = etree.SubElement(root, "drops")
        for drop_type in npc.drop_types:
            rewardlist = etree.SubElement(drops, "rewardlist", type=drop_type.name)

            for group in drop_type.groups:
                group_attrs = {"name": group.name}
                if group.chance is not None:
                    group_attrs["chance"] = str(group.chance)

                group_elem = etree.SubElement(rewardlist, "group", **group_attrs)
                for item in group.items:
                    etree.SubElement(
                        group_elem, "reward",
                        item_id=str(item.id),
                        min=str(item.min_count),
                        max=str(item.max_count),
                        chance=str(item.chance)
                    )

        tree = etree.ElementTree(root)
        tree.write(file_path, encoding="utf-8", pretty_print=True)