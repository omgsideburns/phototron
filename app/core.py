from PySide6.QtWidgets import QMainWindow, QStackedWidget
from app.config import APP_ROOT, CONFIG, LAST_SESSION_FILE, CAMERA_CONFIG, STYLE_CONFIG, STYLE_PATH, STYLE_ROOT, EVENT_BASE_PATH, EVENT_LOADED
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


    # This confirms that the EVENT_LOADED dir exists, if not, build.
    def load_last_session(self):
        if not os.path.exists(EVENT_LOADED):
            print("No Session Path Found", EVENT_LOADED)
        else:
            print("Event Loaded: ", EVENT_LOADED)
        return None
    
    def load_last_session(self):
        if not os.path.exists(EVENT_LOADED):
            print("No session path found:", EVENT_LOADED)
            try:
                os.makedirs(EVENT_LOADED, exist_ok=True)
                print("Created missing event directory:", EVENT_LOADED)
            except Exception as e:
                print("Failed to create event directory:", e)
        else:
            print("Event loaded:", EVENT_LOADED)

    # previously used last_session.txt to remember event directories
    # "session" now describes a users photo session
    # "event" describes the entire group of sessions..
    # example event="halloween part" and sessions are all the times someone hits start on the photo booth.
    # add explanations for all of this in the readme.md