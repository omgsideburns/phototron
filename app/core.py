from PySide6.QtWidgets import QMainWindow, QStackedWidget
from app.config import APP_ROOT, CONFIG, LAST_SESSION_FILE, CAMERA_CONFIG, STYLE_CONFIG, STYLE_PATH
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
        self.main_window = QMainWindow()
        self.stack = QStackedWidget()

        self.main_window.setCentralWidget(self.stack)
        self.main_window.setWindowTitle("📸 Phototron Photo Booth")

        self.current_session_dir = self.load_last_session()

        self.idle_screen = IdleScreen(controller=self)
        self.capture_screen = CaptureScreen(controller=self)
        self.settings_screen = SettingsScreen(controller=self)
        self.email_screen = EmailScreen(controller=self)
        self.preview_screen = PreviewScreen(controller=self)

        self.stack.addWidget(self.idle_screen)
        self.stack.addWidget(self.capture_screen)
        self.stack.addWidget(self.settings_screen)
        self.stack.addWidget(self.email_screen)
        self.stack.addWidget(self.preview_screen)

        self.apply_stylesheet()

        self.stack.setCurrentWidget(self.idle_screen)

        self.camera = CameraManager(CAMERA_CONFIG)

        screen_styles = {
            self.idle_screen: "idle.qss",
            self.capture_screen: "capture.qss",
            self.preview_screen: "preview.qss",
            self.email_screen: "email.qss",
            self.settings_screen: "settings.qss",
        }

        for screen, file_name in screen_styles.items():
            path = os.path.join(APP_ROOT, STYLE_PATH, file_name)
            if os.path.exists(path):
                with open(path, "r") as f:
                    screen.setStyleSheet(f.read())

    def apply_stylesheet(self):
        bg_img = STYLE_CONFIG.get("background_image")

        if bg_img:
            background = os.path.join(APP_ROOT, STYLE_PATH, bg_img)
            self.main_window.setStyleSheet(f"""
                QWidget {{
                    background-image: url("{background}");
                    background-repeat: no-repeat;
                    background-position: center;
                    background-attachment: fixed;
                }}
                """)

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
