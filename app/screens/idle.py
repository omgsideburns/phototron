from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
)

from app.widgets.slideshow import SlideshowWidget
import app.lights


class IdleScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setBaseSize(480, 640)

        # Slideshow..
        self.slideshow = SlideshowWidget(self)
        ssw = self.width()
        ssh = self.height()

        def calculate_dimensions(container_width, container_height):
            ratio = 3 / 2
            height = container_height * 0.8
            width = container_height / ratio
            return width, height

        w, h = calculate_dimensions(ssw, ssh)
        self.slideshow.setBaseSize
        self.slideshow.setFixedSize(w, h)

        # Start button..
        self.start_button = QPushButton("START")
        self.start_button.setObjectName("StartButton")
        # self.start_button.setFixedSize(360,30)
        self.start_button.clicked.connect(self.start_pressed)

        # Settings button..
        self.settings_button = QPushButton("")
        self.settings_button.setObjectName("SettingsButton")
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.setParent(self)
        self.settings_button.setFlat(True)
        self.settings_button.move(0, 0)
        self.settings_button.raise_()
        self.settings_button.clicked.connect(self.open_settings)

        # Build overlay layout
        self.overlay_layout = QVBoxLayout()   
    
        # Final layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.slideshow, stretch=0)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.start_button, stretch=1)
        self.setLayout(main_layout)

        # initiate lights
        app.lights.idle()

    # Define the button actions
    def start_pressed(self):
        print("START pressed")
        self.controller.capture_screen.start_sequence()
        self.controller.go_to(self.controller.capture_screen)

    def open_settings(self):
        print("Opening Settings")
        self.controller.go_to(self.controller.settings_screen)

    def resizeEvent(self, event):
        super().resizeEvent(None)
        ssw = self.width()
        ssh = self.height()

        def calculate_dimensions(container_width, container_height):
            ratio = 3 / 2
            height = container_height * 0.8
            width = height / ratio
            return width, height

        w, h = calculate_dimensions(ssw, ssh)
        self.slideshow.setFixedSize(w, h)
