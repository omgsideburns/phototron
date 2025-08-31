from PySide6.QtWidgets import QMainWindow, QStackedWidget
from app.config import APP_ROOT, CONFIG, LAST_SESSION_FILE, CAMERA_CONFIG, STYLE_CONFIG, STYLE_PATH, STYLE_ROOT, EVENT_BASE_PATH
from app.screens.idle import IdleScreen
from app.screens.capture import CaptureScreen
from app.screens.settings import SettingsScreen
from app.screens.email import EmailScreen
from app.camera import CameraManager
from app.screens.preview import PreviewScreen
import os

class AppController:
    def __init__(self):
        self.config = CONFIG
        self.current_session_dir = self.load_last_session()
        print("current_session_dir: ", self.current_session_dir)
        self.camera = CameraManager(CAMERA_CONFIG)

        # assign screens
        self.idle_screen = IdleScreen(controller=self)
        self.capture_screen = CaptureScreen(controller=self)
        self.settings_screen = SettingsScreen(controller=self)
        self.email_screen = EmailScreen(controller=self)
        self.preview_screen = PreviewScreen(controller=self)

        # build the stack of pidgies
        self.stack = QStackedWidget()
        self.stack.addWidget(self.idle_screen)
        self.stack.addWidget(self.capture_screen)
        self.stack.addWidget(self.settings_screen)
        self.stack.addWidget(self.email_screen)
        self.stack.addWidget(self.preview_screen)
        self.stack.setCurrentWidget(self.idle_screen)

        self.main_window = QMainWindow()
        self.main_window.setCentralWidget(self.stack)
        self.main_window.setWindowTitle("📸 Phototron Photo Booth")

        # bring in the selected style..
        sshFile = os.path.join(STYLE_PATH, "style.qss")
        with open(sshFile,"r") as f:
            shh = (
                f.read()
                .replace("{{style_path}}", STYLE_PATH)
            )
            self.main_window.setStyleSheet(shh)

    def widget(self):
        return self.main_window

    def go_to(self, screen):
        self.stack.setCurrentWidget(screen)

    def load_last_session(self):
        try:
            with open(LAST_SESSION_FILE, "r") as f:
                path = f.read().strip()
                if os.path.exists(path):
                    return path
        except FileNotFoundError:
            pass
        return None

    def save_last_session(self, path):
        with open(LAST_SESSION_FILE, "w") as f:
            f.write(path)
        self.current_session_dir = path