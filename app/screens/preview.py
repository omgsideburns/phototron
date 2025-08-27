from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from app.emailer import send_email
from app.print import send_to_printer
import os

class PreviewScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_photo_path = None

        self.layout = QVBoxLayout()
        self.photo_label = QLabel("Photo will appear here")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.photo_label)

        # Print group container
        self.print_group = QWidget()
        print_layout = QVBoxLayout()
        self.print_prompt = QLabel("🖨️ Would you like to print this photo?")
        self.print_prompt.setAlignment(Qt.AlignCenter)

        print_button_row = QHBoxLayout()
        self.print_yes_btn = QPushButton("Yes ✅")
        self.print_no_btn = QPushButton("No ❌")
        self.print_yes_btn.clicked.connect(self.handle_print_yes)
        self.print_no_btn.clicked.connect(self.handle_print_no)
        print_button_row.addWidget(self.print_yes_btn)
        print_button_row.addWidget(self.print_no_btn)

        print_layout.addWidget(self.print_prompt)
        print_layout.addLayout(print_button_row)
        self.print_group.setLayout(print_layout)
        self.layout.addWidget(self.print_group)

        # Email group container (hidden initially)
        self.email_group = QWidget()
        email_layout = QVBoxLayout()
        self.email_prompt = QLabel("📧 Would you like to email this photo?")
        self.email_prompt.setAlignment(Qt.AlignCenter)

        email_button_row = QHBoxLayout()
        self.email_yes_btn = QPushButton("Yes ✅")
        self.email_no_btn = QPushButton("No ❌")
        self.email_yes_btn.clicked.connect(self.handle_email_yes)
        self.email_no_btn.clicked.connect(self.handle_email_no)
        email_button_row.addWidget(self.email_yes_btn)
        email_button_row.addWidget(self.email_no_btn)

        email_layout.addWidget(self.email_prompt)
        email_layout.addLayout(email_button_row)
        self.email_group.setLayout(email_layout)
        self.email_group.setVisible(False)
        self.layout.addWidget(self.email_group)

        self.setLayout(self.layout)
        self.original_pixmap = None

    def load_photo(self, filepath):
        self.current_photo_path = filepath
        if os.path.exists(filepath):
            self.original_pixmap = QPixmap(filepath)
            self.update_photo_label()
        else:
            self.photo_label.setText("❌ Could not load photo")

    def update_photo_label(self):
        if self.original_pixmap:
            scaled = self.original_pixmap.scaled(
                self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_photo_label()

    def handle_print_yes(self):
        if self.current_photo_path:
            print("🖨️ Printing photo...")
            success = send_to_printer(self.current_photo_path)
            if not success:
                print("⚠️ Print failed.")
        else:
            print("⚠️ No photo to print.")

    def handle_print_no(self):
        print("⏭️ Skipping print")
        self.hide_print_prompt()
        self.show_email_prompt()

    def hide_print_prompt(self):
        self.print_group.setVisible(False)

    def show_email_prompt(self):
        self.email_group.setVisible(True)

    def handle_email_yes(self):
        print("📧 Emailing photo...")
        to_email = "pcx.tony@gmail.com"  # Replace this later with actual user input
        image_path = self.current_photo_path     # Assuming `self.loaded_path` holds the last composite image path
        send_email(to_email, image_path)        
        self.controller.go_to(self.controller.idle_screen)

    def handle_email_no(self):
        print("❌ Skipping email")
        self.controller.go_to(self.controller.idle_screen)