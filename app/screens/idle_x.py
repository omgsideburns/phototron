# idle.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from app.widgets.slideshow import SlideshowWidget
import lights

class IdleScreenUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(800, 600)

        # slideshow
        self.slideshow = SlideshowWidget(self)

        # overlay layout
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("START")
        self.start_button.setMinimumHeight(80)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setMinimumHeight(60)

        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.settings_button)


class IdleScreenLogic:
    def __init__(self, ui: IdleScreenUI, controller):
        self.ui = ui
        self.controller = controller
        lights.idle_a
        lights.idle_b

        self.ui.start_button.clicked.connect(self.start_pressed)
        self.ui.settings_button.clicked.connect(self.open_settings)          

    def start_pressed(self):
        print("START pressed")
        self.controller.capture_screen.start_sequence()
        self.controller.go_to(self.controller.capture_screen)

    def open_settings(self):
        print("Opening Settings")
        self.controller.go_to(self.controller.settings_screen)


# Optional: glue class if needed by app controller
class IdleScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.ui = IdleScreenUI()
        self.logic = IdleScreenLogic(self.ui, controller)

        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.setLayout(layout)