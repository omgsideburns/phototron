from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QStackedLayout

from app.widgets.slideshow import SlideshowWidget
from app.config import SETTINGS_CONFIG

class IdleScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setMinimumSize(800, 600)

        # Background Slideshow
        self.slideshow = SlideshowWidget(self)

        # Overlay layout
        self.overlay_layout = QVBoxLayout()
        self.overlay_layout.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("START")
        self.start_button.setMinimumHeight(80)
        self.start_button.clicked.connect(self.start_pressed)

        self.overlay_layout.addWidget(self.start_button)

        if SETTINGS_CONFIG.get("visible", False):
            self.settings_button = QPushButton("Settings")
            self.settings_button.setMinimumHeight(60)
            self.settings_button.clicked.connect(self.open_settings)
            self.overlay_layout.addWidget(self.settings_button)

        # Final layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.slideshow)
        main_layout.addLayout(self.overlay_layout)
        self.setLayout(main_layout)

    def start_pressed(self):
        print("START pressed")
        self.controller.capture_screen.start_sequence()
        self.controller.go_to(self.controller.capture_screen)

    def open_settings(self):
        print("Opening Settings")
        self.controller.go_to(self.controller.settings_screen)