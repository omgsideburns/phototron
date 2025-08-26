from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

class PreviewScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.current_photo_path = None

        self.layout = QVBoxLayout()
        self.photo_label = QLabel("Photo will appear here")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.photo_label)

        button_row = QHBoxLayout()
        self.yes_btn = QPushButton("Print ✅")
        self.no_btn = QPushButton("Skip ❌")
        self.yes_btn.clicked.connect(self.print_yes)
        self.no_btn.clicked.connect(self.print_no)
        button_row.addWidget(self.yes_btn)
        button_row.addWidget(self.no_btn)

        self.layout.addLayout(button_row)
        self.setLayout(self.layout)

    def load_photo(self, filepath):
        self.current_photo_path = filepath
        if os.path.exists(filepath):
            pixmap = QPixmap(filepath).scaled(3600, 2400, Qt.KeepAspectRatio)
            self.photo_label.setPixmap(pixmap)
        else:
            self.photo_label.setText("❌ Could not load photo")

    def print_yes(self):
        print(f"🖨️ Sending to printer: {self.current_photo_path}")
        # TODO: Implement actual print command
        self.controller.go_to(self.controller.email_screen)

    def print_no(self):
        print("⏭️ Skipping print")
        self.controller.go_to(self.controller.email_screen)