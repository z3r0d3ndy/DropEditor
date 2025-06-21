import os
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog,
    QHBoxLayout, QLabel, QComboBox, QCheckBox, QGroupBox,
    QSpinBox, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from pathlib import Path
from typing import List
import time
from threading import Thread

from core.parser import load_npcs_from_folder, get_unique_npc_types, save_npcs_to_folder
from core.editor import DropEditor
from core.history import History
from .tree_view import DropTreeWidget
from .loading_widget import LoadingWidget
from .add_drop_dialog import AddDropDialog


class DropEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.npcs = []
        self.filtered_npcs = []
        self.editor = None
        self.history = History()
        self.last_folder = ""
        self.loading_widget = LoadingWidget(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Lineage 2 Drop Editor")
        self.setGeometry(100, 100, 1400, 900)

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header = QLabel()
        if os.path.exists("resources/header.png"):
            header.setPixmap(QPixmap("resources/header.png").scaled(512, 100))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Control buttons
        controls_top = QHBoxLayout()

        self.btn_open = QPushButton("Open XML Folder")
        self.btn_open.clicked.connect(self.open_folder)
        controls_top.addWidget(self.btn_open)

        self.btn_clear = QPushButton("Clear All Drops")
        self.btn_clear.clicked.connect(self.clear_drops)
        self.btn_clear.setEnabled(False)
        controls_top.addWidget(self.btn_clear)

        self.btn_adena = QPushButton("Keep Only Adena")
        self.btn_adena.clicked.connect(self.keep_adena)
        self.btn_adena.setEnabled(False)
        controls_top.addWidget(self.btn_adena)

        self.btn_undo = QPushButton("Undo (Ctrl+Z)")
        self.btn_undo.setShortcut("Ctrl+Z")
        self.btn_undo.clicked.connect(self.undo_action)
        self.btn_undo.setEnabled(False)
        controls_top.addWidget(self.btn_undo)

        self.btn_add_drop = QPushButton("Add Drop")
        self.btn_add_drop.clicked.connect(self.show_add_drop_dialog)
        self.btn_add_drop.setEnabled(False)
        controls_top.addWidget(self.btn_add_drop)

        self.btn_save = QPushButton("Save All")
        self.btn_save.clicked.connect(self.save_all)
        self.btn_save.setEnabled(False)
        controls_top.addWidget(self.btn_save)

        self.btn_save_as = QPushButton("Save As...")
        self.btn_save_as.clicked.connect(self.save_as)
        self.btn_save_as.setEnabled(False)
        controls_top.addWidget(self.btn_save_as)

        main_layout.addLayout(controls_top)

        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout()

        # NPC Type filter
        self.type_filter = QComboBox()
        self.type_filter.addItem("All NPC Types")
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(QLabel("NPC Type:"))
        filters_layout.addWidget(self.type_filter)

        # Level filter
        level_group = QGroupBox("Level")
        level_layout = QHBoxLayout()

        self.level_min = QSpinBox()
        self.level_min.setRange(0, 100)
        self.level_min.setValue(0)
        self.level_min.valueChanged.connect(self.apply_filters)
        level_layout.addWidget(QLabel("From:"))
        level_layout.addWidget(self.level_min)

        self.level_max = QSpinBox()
        self.level_max.setRange(0, 100)
        self.level_max.setValue(100)
        self.level_max.valueChanged.connect(self.apply_filters)
        level_layout.addWidget(QLabel("To:"))
        level_layout.addWidget(self.level_max)

        level_group.setLayout(level_layout)
        filters_layout.addWidget(level_group)

        # Drop filters
        self.filter_empty = QCheckBox("Hide NPCs with no drops")
        self.filter_empty.stateChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.filter_empty)

        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search NPC by name or ID...")
        self.search_box.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(QLabel("Search:"))
        filters_layout.addWidget(self.search_box)

        filters_group.setLayout(filters_layout)
        main_layout.addWidget(filters_group)

        # Tree view
        self.tree = DropTreeWidget()
        self.tree.itemDoubleClicked.connect(self.handle_item_edit)
        main_layout.addWidget(self.tree)

        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)

        # Set main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select XML Folder")
        if folder:
            self.last_folder = folder
            self.loading_widget.start()

            # Load in background thread
            self.worker_thread = Thread(
                target=self.load_npcs_background,
                args=(Path(folder),)
            )
            self.worker_thread.start()

    def load_npcs_background(self, folder_path):
        npcs = load_npcs_from_folder(folder_path)
        QTimer.singleShot(0, lambda: self.folder_loaded(npcs))

    def folder_loaded(self, npcs):
        self.npcs = npcs
        self.editor = DropEditor(self.npcs)
        self.history.add_state(self.npcs)
        self.update_type_filter()
        self.apply_filters()

        # Enable buttons
        self.btn_clear.setEnabled(True)
        self.btn_adena.setEnabled(True)
        self.btn_undo.setEnabled(False)
        self.btn_add_drop.setEnabled(True)
        self.btn_save.setEnabled(True)
        self.btn_save_as.setEnabled(True)

        self.status_label.setText(f"Loaded {len(self.npcs)} NPCs")
        self.loading_widget.stop()

    def update_type_filter(self):
        self.type_filter.clear()
        self.type_filter.addItem("All NPC Types")
        unique_types = get_unique_npc_types(self.npcs)
        for npc_type in unique_types:
            self.type_filter.addItem(npc_type)

    def apply_filters(self):
        self.loading_widget.start()
        QTimer.singleShot(100, self._apply_filters_async)

    def _apply_filters_async(self):
        self.filtered_npcs = []
        selected_type = self.type_filter.currentText()
        min_level = self.level_min.value()
        max_level = self.level_max.value()
        search_text = self.search_box.text().lower()
        hide_empty = self.filter_empty.isChecked()

        for npc in self.npcs:
            # Apply filters
            if selected_type != "All NPC Types" and npc.npc_type != selected_type:
                continue
            if not (min_level <= npc.level <= max_level):
                continue
            if search_text and (search_text not in str(npc.id).lower() and
                                search_text not in npc.name.lower()):
                continue
            if hide_empty and not npc.drop_types:
                continue

            self.filtered_npcs.append(npc)

        self.tree.display_npcs(self.filtered_npcs)
        self.status_label.setText(f"Displaying {len(self.filtered_npcs)} of {len(self.npcs)} NPCs")
        self.loading_widget.stop()

    def undo_action(self):
        prev_state = self.history.undo()
        if prev_state:
            self.npcs = prev_state
            self.editor = DropEditor(self.npcs)
            self.apply_filters()
            self.btn_undo.setEnabled(self.history.can_undo())
            self.status_label.setText("Undo successful!")
            QTimer.singleShot(2000, lambda: self.status_label.setText(
                f"Displaying {len(self.filtered_npcs)} of {len(self.npcs)} NPCs"))

    def show_add_drop_dialog(self):
        npc_types = [self.type_filter.itemText(i) for i in range(1, self.type_filter.count())]
        dialog = AddDropDialog(self, npc_types)
        if dialog.exec():
            values = dialog.get_values()
            self.history.add_state(self.npcs)
            self.editor.add_drop_items(
                values["npc_ids"],
                values["levels"],
                values["npc_types"],
                values["drop_type"],
                values["group_name"],
                values["group_chance"],
                values["items"]
            )
            self.apply_filters()
            self.btn_undo.setEnabled(True)

    def clear_drops(self):
        npc_types = [self.type_filter.itemText(i) for i in range(1, self.type_filter.count())]
        dialog = AddDropDialog(self, npc_types)
        dialog.setWindowTitle("Clear Drops - Select NPC Types")
        # Hide unnecessary elements
        for widget in [dialog.drop_group, dialog.items_group]:
            widget.hide()

        if dialog.exec():
            values = dialog.get_values()
            self.history.add_state(self.npcs)
            self.editor.clear_all_drops(
                npc_types=values["npc_types"],
                min_level=values["levels"][0],
                max_level=values["levels"][1]
            )
            self.apply_filters()
            self.btn_undo.setEnabled(True)

    def keep_adena(self):
        npc_types = [self.type_filter.itemText(i) for i in range(1, self.type_filter.count())]
        dialog = AddDropDialog(self, npc_types)
        dialog.setWindowTitle("Keep Only Adena - Select NPC Types")
        # Hide unnecessary elements
        for widget in [dialog.drop_group, dialog.items_group]:
            widget.hide()

        if dialog.exec():
            values = dialog.get_values()
            self.history.add_state(self.npcs)
            self.editor.clear_all_except_adena(
                npc_types=values["npc_types"],
                min_level=values["levels"][0],
                max_level=values["levels"][1]
            )
            self.apply_filters()
            self.btn_undo.setEnabled(True)

    def save_all(self):
        if self.last_folder:
            self._save_files(self.npcs, Path(self.last_folder))

    def save_as(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if folder:
            self._save_files(self.npcs, Path(folder))

    def _save_files(self, npcs: List[NPC], folder: Path):
        self.loading_widget.start()
        self.status_label.setText("Saving files...")

        # Save in background thread
        self.save_thread = Thread(
            target=self._save_files_thread,
            args=(npcs, folder)
        )
        self.save_thread.start()

        # Check for completion
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(lambda: self._check_save_complete(self.save_thread))
        self.save_timer.start(100)

    def _save_files_thread(self, npcs: List[NPC], folder: Path):
        save_npcs_to_folder(npcs, folder)

    def _check_save_complete(self, thread):
        if not thread.is_alive():
            self.save_timer.stop()
            self.loading_widget.stop()
            self.status_label.setText("Save completed!")
            QTimer.singleShot(2000, lambda: self.status_label.setText(
                f"Displaying {len(self.filtered_npcs)} of {len(self.npcs)} NPCs"))

    def handle_item_edit(self, npc, drop_type, group, item):
        """Обрабатывает редактирование элементов дропа по двойному клику"""
        self.history.add_state(self.npcs)

        if drop_type and not group and not item:
            # Редактирование DropType
            reply = QMessageBox.question(
                self, 'Delete Drop Type',
                f"Delete all drops of type {drop_type.name} from {npc.name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.editor.remove_drop_type(npc, drop_type.name)
                self.apply_filters()

        elif group and not item:
            # Редактирование DropGroup
            if group.chance is not None:
                dialog = EditDropDialog(self, "Edit Group Chance", {
                    "chance": {
                        "label": "Group Chance:",
                        "type": "float",
                        "value": group.chance,
                        "min": 0,
                        "max": 1000000
                    }
                })
                if dialog.exec():
                    values = dialog.get_values()
                    self.editor.update_drop_group(
                        npc, drop_type.name, group.name, values["chance"]
                    )
                    self.apply_filters()
            else:
                QMessageBox.information(self, "Info", "This group has no chance to edit")

        elif group and item == "delete":
            # Удаление группы
            reply = QMessageBox.question(
                self, 'Delete Group',
                f"Delete group {group.name} from {npc.name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.editor.remove_drop_group(npc, drop_type.name, group.name)
                self.apply_filters()

        elif item:
            # Редактирование предмета
            dialog = EditDropDialog(self, "Edit Drop Item", {
                "id": {
                    "label": "Item ID:",
                    "type": "int",
                    "value": item.id,
                    "min": 0,
                    "max": 1000000
                },
                "min": {
                    "label": "Min Count:",
                    "type": "int",
                    "value": item.min_count,
                    "min": 1,
                    "max": 10000
                },
                "max": {
                    "label": "Max Count:",
                    "type": "int",
                    "value": item.max_count,
                    "min": 1,
                    "max": 10000
                },
                "chance": {
                    "label": "Drop Chance:",
                    "type": "float",
                    "value": item.chance,
                    "min": 0,
                    "max": 1000000
                }
            })

            if dialog.exec():
                values = dialog.get_values()
                self.editor.update_drop_item(
                    npc, drop_type.name, group.name,
                    item.id, values["id"], values["min"], values["max"], values["chance"]
                )
                self.apply_filters()

        self.btn_undo.setEnabled(True)