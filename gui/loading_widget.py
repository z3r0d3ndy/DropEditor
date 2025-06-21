from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie


class LoadingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Loading...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.movie = QMovie("resources/loading.gif")
        self.loading_label = QLabel()
        self.loading_label.setMovie(self.movie)
        layout.addWidget(self.loading_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_completion)

    def start(self):
        self.movie.start()
        self.show()
        self.timer.start(100)

    def stop(self):
        self.movie.stop()
        self.hide()
        self.timer.stop()

    def check_completion(self):
        if not self.isVisible():
            self.stop()