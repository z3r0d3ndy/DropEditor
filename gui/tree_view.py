from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import NPC


class DropTreeWidget(QTreeWidget):
    itemDoubleClicked = pyqtSignal(object, object, object, object)  # npc, drop_type, group, item

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["NPC", "Level", "Type", "Drop Info"])
        self.setColumnCount(4)
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def display_npcs(self, npcs: list[NPC]):
        self.clear()
        self.npcs = npcs

        for npc in npcs:
            npc_item = QTreeWidgetItem(self)
            npc_item.setText(0, f"{npc.name} (ID: {npc.id})")
            npc_item.setText(1, str(npc.level))
            npc_item.setText(2, npc.npc_type)
            npc_item.setData(0, Qt.ItemDataRole.UserRole, (npc, None, None, None))

            if not npc.drop_types:
                npc_item.setText(3, "No drops")
                continue

            for drop_type in npc.drop_types:
                type_item = QTreeWidgetItem(npc_item)
                type_item.setText(3, f"Drop Type: {drop_type.name}")
                type_item.setData(0, Qt.ItemDataRole.UserRole, (npc, drop_type, None, None))

                for group in drop_type.groups:
                    group_text = f"Group: {group.name}"
                    if group.chance is not None:
                        group_text += f" (Chance: {group.chance})"

                    group_item = QTreeWidgetItem(type_item)
                    group_item.setText(3, group_text)
                    group_item.setData(0, Qt.ItemDataRole.UserRole, (npc, drop_type, group, None))

                    for item in group.items:
                        item_item = QTreeWidgetItem(group_item)
                        item_text = (f"Item ID: {item.id}, Count: {item.min_count}-{item.max_count}, "
                                     f"Chance: {item.chance}")
                        item_item.setText(3, item_text)
                        item_item.setData(0, Qt.ItemDataRole.UserRole, (npc, drop_type, group, item))

        self.resizeColumnToContents(0)

    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item:
            return

        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        npc, drop_type, group, drop_item = data
        menu = QMenu()

        if drop_type and not group and not drop_item:
            # Drop Type level
            menu.addAction("Delete Drop Type", lambda: self.delete_drop_type(npc, drop_type))
        elif group and not drop_item:
            # Group level
            menu.addAction("Edit Group Chance", lambda: self.edit_group_chance(npc, drop_type, group))
            menu.addAction("Delete Group", lambda: self.delete_group(npc, drop_type, group))
        elif drop_item:
            # Item level
            menu.addAction("Edit Item", lambda: self.edit_item(npc, drop_type, group, drop_item))

        if menu.actions():
            menu.exec(self.viewport().mapToGlobal(pos))

    def delete_drop_type(self, npc, drop_type):
        self.itemDoubleClicked.emit(npc, drop_type, None, None)

    def edit_group_chance(self, npc, drop_type, group):
        self.itemDoubleClicked.emit(npc, drop_type, group, None)

    def delete_group(self, npc, drop_type, group):
        self.itemDoubleClicked.emit(npc, drop_type, group, "delete")

    def edit_item(self, npc, drop_type, group, item):
        self.itemDoubleClicked.emit(npc, drop_type, group, item)