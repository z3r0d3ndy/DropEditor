from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QDialogButtonBox, QComboBox, QCheckBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt


class AddDropDialog(QDialog):
    def __init__(self, parent=None, npc_types=None):
        super().__init__(parent)
        self.setWindowTitle("Add Drop Items")
        self.setMinimumWidth(600)
        self.npc_types = npc_types or []
        self.items = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # NPC Selection Group
        self.npc_group = QGroupBox("NPC Selection")
        npc_layout = QVBoxLayout()

        # NPC IDs
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("NPC IDs (comma separated):"))
        self.npc_ids_edit = QLineEdit()
        id_layout.addWidget(self.npc_ids_edit)
        npc_layout.addLayout(id_layout)

        # Levels
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Level Range:"))

        self.level_min = QSpinBox()
        self.level_min.setRange(0, 100)
        self.level_min.setValue(0)
        level_layout.addWidget(self.level_min)

        level_layout.addWidget(QLabel("to"))

        self.level_max = QSpinBox()
        self.level_max.setRange(0, 100)
        self.level_max.setValue(100)
        level_layout.addWidget(self.level_max)

        npc_layout.addLayout(level_layout)

        # NPC Types
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("NPC Types:"))

        self.type_combo = QComboBox()
        self.type_combo.addItem("All Types")
        self.type_combo.addItems(self.npc_types)
        type_layout.addWidget(self.type_combo)

        npc_layout.addLayout(type_layout)
        self.npc_group.setLayout(npc_layout)
        layout.addWidget(self.npc_group)

        # Drop Settings Group
        self.drop_group = QGroupBox("Drop Settings")
        drop_layout = QVBoxLayout()

        # Drop Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Drop Type:"))

        self.drop_type_combo = QComboBox()
        self.drop_type_combo.addItems(["SWEEP", "RATED_GROUPS", "NOT_RATED_GROUPS"])
        type_layout.addWidget(self.drop_type_combo)

        drop_layout.addLayout(type_layout)

        # Group Name
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("Group Name:"))

        self.group_name_edit = QLineEdit("New Group")
        group_layout.addWidget(self.group_name_edit)

        drop_layout.addLayout(group_layout)

        # Group Chance
        self.group_chance_check = QCheckBox("Has Group Chance (for RATED_GROUPS)")
        self.group_chance_check.setChecked(True)
        drop_layout.addWidget(self.group_chance_check)

        self.group_chance_edit = QDoubleSpinBox()
        self.group_chance_edit.setRange(0, 1000000)
        self.group_chance_edit.setValue(1000)
        self.group_chance_edit.setEnabled(True)
        self.group_chance_check.stateChanged.connect(
            lambda: self.group_chance_edit.setEnabled(self.group_chance_check.isChecked()))

        chance_layout = QHBoxLayout()
        chance_layout.addWidget(QLabel("Group Chance:"))
        chance_layout.addWidget(self.group_chance_edit)
        drop_layout.addLayout(chance_layout)

        self.drop_group.setLayout(drop_layout)
        layout.addWidget(self.drop_group)

        # Items Group
        self.items_group = QGroupBox("Items")
        items_layout = QVBoxLayout()

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Item ID", "Min", "Max", "Chance"])
        self.items_table.setRowCount(1)

        for col in range(4):
            if col == 0 or col == 3:  # ID and Chance
                spin = QSpinBox()
                spin.setRange(0, 1000000)
                if col == 3:
                    spin.setValue(1000)
                self.items_table.setCellWidget(0, col, spin)
            else:  # Min and Max
                spin = QSpinBox()
                spin.setRange(1, 10000)
                spin.setValue(1)
                self.items_table.setCellWidget(0, col, spin)

        table_buttons = QHBoxLayout()
        add_row_btn = QPushButton("Add Row")
        add_row_btn.clicked.connect(self.add_item_row)
        table_buttons.addWidget(add_row_btn)

        del_row_btn = QPushButton("Delete Row")
        del_row_btn.clicked.connect(self.del_item_row)
        table_buttons.addWidget(del_row_btn)

        items_layout.addWidget(self.items_table)
        items_layout.addLayout(table_buttons)
        self.items_group.setLayout(items_layout)
        layout.addWidget(self.items_group)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def add_item_row(self):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        for col in range(4):
            if col == 0 or col == 3:  # ID and Chance
                spin = QSpinBox()
                spin.setRange(0, 1000000)
                if col == 3:
                    spin.setValue(1000)
                self.items_table.setCellWidget(row, col, spin)
            else:  # Min and Max
                spin = QSpinBox()
                spin.setRange(1, 10000)
                spin.setValue(1)
                self.items_table.setCellWidget(row, col, spin)

    def del_item_row(self):
        row = self.items_table.currentRow()
        if row >= 0:
            self.items_table.removeRow(row)

    def validate(self):
        try:
            # Parse NPC IDs
            npc_ids = []
            ids_text = self.npc_ids_edit.text().strip()
            if ids_text:
                npc_ids = [int(id_str.strip()) for id_str in ids_text.split(",")]

            # Get levels
            min_level = self.level_min.value()
            max_level = self.level_max.value()
            if min_level > max_level:
                raise ValueError("Min level cannot be greater than max level")

            # Get NPC types
            npc_types = []
            selected_type = self.type_combo.currentText()
            if selected_type != "All Types":
                npc_types = [selected_type]

            # Get drop settings
            drop_type = self.drop_type_combo.currentText()
            group_name = self.group_name_edit.text().strip()
            if not group_name:
                raise ValueError("Group name cannot be empty")

            group_chance = None
            if self.group_chance_check.isChecked():
                group_chance = self.group_chance_edit.value()

            # Get items
            items = []
            for row in range(self.items_table.rowCount()):
                item_id = self.items_table.cellWidget(row, 0).value()
                min_count = self.items_table.cellWidget(row, 1).value()
                max_count = self.items_table.cellWidget(row, 2).value()
                chance = self.items_table.cellWidget(row, 3).value()

                if min_count > max_count:
                    raise ValueError(f"Min count cannot be greater than max count (row {row + 1})")

                items.append({
                    "id": item_id,
                    "min": min_count,
                    "max": max_count,
                    "chance": chance
                })

            if not items:
                raise ValueError("At least one item must be added")

            self.npc_ids = npc_ids
            self.levels = (min_level, max_level)
            self.npc_types = npc_types
            self.drop_type = drop_type
            self.group_name = group_name
            self.group_chance = group_chance
            self.items = items

            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def get_values(self):
        return {
            "npc_ids": self.npc_ids,
            "levels": self.levels,
            "npc_types": self.npc_types,
            "drop_type": self.drop_type,
            "group_name": self.group_name,
            "group_chance": self.group_chance,
            "items": self.items
        }