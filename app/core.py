from PySide6.QtWidgets import QStackedWidget
from app.screens.idle import IdleScreen
from app.screens.capture import CaptureScreen  # ⬅️ NEW
from app.screens.settings import SettingsScreen
from app.camera import CameraManager
import os

class AppController:
    def __init__(self):
        self.stack = QStackedWidget()

        self.current_session_dir = self.load_last_session()

        self.idle_screen = IdleScreen(controller=self)
        self.capture_screen = CaptureScreen(controller=self)
        self.settings_screen = SettingsScreen(controller=self)
        
        self.stack.addWidget(self.idle_screen)
        self.stack.addWidget(self.capture_screen)
        self.stack.addWidget(self.settings_screen)

        self.stack.setCurrentWidget(self.idle_screen)

        self.camera = CameraManager()

    def widget(self):
        return self.stack

    def go_to(self, screen):
        self.stack.setCurrentWidget(screen)

    def load_last_session(self):
        try:
            with open("phototron/assets/last_session.txt", "r") as f:
                path = f.read().strip()
                if os.path.exists(path):
                    return path
        except FileNotFoundError:
            pass
        return None

    def save_last_session(self, path):
        with open("phototron/assets/last_session.txt", "w") as f:
            f.write(path)
        self.current_session_dir = path