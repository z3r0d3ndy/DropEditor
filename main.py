import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import DropEditorWindow

def main():
    app = QApplication(sys.argv)
    window = DropEditorWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()