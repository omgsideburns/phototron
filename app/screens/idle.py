from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel

class IdleScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Idle / Attract Mode"))

        start_button = QPushButton("START")
        start_button.setMinimumHeight(80)
        start_button.clicked.connect(self.start_pressed)
        layout.addWidget(start_button)

        settings_button = QPushButton("Settings")
        settings_button.setMinimumHeight(60)
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button)

        self.setLayout(layout)

    def start_pressed(self):
        print("START pressed")
        self.controller.capture_screen.start_sequence()
        self.controller.go_to(self.controller.capture_screen)

    def open_settings(self):
        print("Opening Settings")
        self.controller.go_to(self.controller.settings_screen)