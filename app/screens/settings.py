from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QMessageBox
from PySide6.QtCore import Qt
from app.config import APP_ROOT, CONFIG, LAST_SESSION_FILE, EVENT_BASE_PATH
import os

class SettingsScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Settings")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("📁 Current Session:"))
        self.current_label = QLabel("(None)")
        layout.addWidget(self.current_label)

        layout.addWidget(QLabel("🔤 Create New Session:"))
        self.session_name_input = QLineEdit()
        layout.addWidget(self.session_name_input)

        create_button = QPushButton("Create Session")
        create_button.clicked.connect(self.create_session)
        layout.addWidget(create_button)

        layout.addWidget(QLabel("📜 Load Existing Session:"))
        self.session_list = QListWidget()
        self.session_list.itemDoubleClicked.connect(self.load_session)
        layout.addWidget(self.session_list)

        back_button = QPushButton("⬅️ Back")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.refresh_session_list()
        self.update_current_label()

    def refresh_session_list(self):
        self.session_list.clear()
        if not os.path.exists(EVENT_BASE_PATH):
            os.makedirs(EVENT_BASE_PATH)
        for name in os.listdir(EVENT_BASE_PATH):
            full_path = os.path.join(EVENT_BASE_PATH, name)
            if os.path.isdir(full_path):
                self.session_list.addItem(name)

    def update_current_label(self):
        current = self.controller.current_session_dir
        self.current_label.setText(current if current else "(None)")

    def create_session(self):
        name = self.session_name_input.text().strip().replace(" ", "_")
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a session name.")
            return
        full_path = os.path.join(EVENT_BASE_PATH, name)
        try:
            os.makedirs(full_path, exist_ok=False)
        except FileExistsError:
            QMessageBox.warning(self, "Error", "Session already exists.")
            return
        self.controller.save_last_session(full_path)
        self.update_current_label()
        self.refresh_session_list()

    def load_session(self, item):
        name = item.text()
        full_path = os.path.join(EVENT_BASE_PATH, name)
        self.controller.save_last_session(full_path)
        self.update_current_label()

    def go_back(self):
        self.controller.go_to(self.controller.idle_screen)
