from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QDialogButtonBox, QMessageBox
)


class EditDropDialog(QDialog):
    def __init__(self, parent=None, title="Edit", fields=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.fields = fields or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.widgets = {}

        for name, config in self.fields.items():
            label = QLabel(config["label"])
            layout.addWidget(label)

            if config["type"] == "int":
                widget = QSpinBox()
                widget.setRange(config.get("min", 0), config.get("max", 1000000))
                widget.setValue(config["value"])
            elif config["type"] == "float":
                widget = QDoubleSpinBox()
                widget.setRange(config.get("min", 0), config.get("max", 1000000))
                widget.setValue(config["value"])
                widget.setDecimals(5)
            else:
                widget = QLineEdit(str(config["value"]))

            self.widgets[name] = widget
            layout.addWidget(widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validate)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate(self):
        try:
            for name, config in self.fields.items():
                widget = self.widgets[name]
                if config["type"] in ["int", "float"]:
                    float(widget.value())
                else:
                    str(widget.text())
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Invalid value: {e}")

    def get_values(self):
        values = {}
        for name, config in self.fields.items():
            widget = self.widgets[name]
            if config["type"] == "int":
                values[name] = widget.value()
            elif config["type"] == "float":
                values[name] = widget.value()
            else:
                values[name] = widget.text()
        return values