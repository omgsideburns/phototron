from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from app.emailer import send_email
from app.print import send_to_printer


class PreviewScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_photo_path: Path | None = None
        self.original_pixmap: QPixmap | None = None

        # Layout
        self.layout = QVBoxLayout()
        self.photo_label = QLabel("Photo will appear here")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.photo_label)

        # Print group
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

        # Email group (hidden initially)
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

    def load_photo(self, filepath: str | Path) -> None:
        path = Path(filepath)
        self.current_photo_path = path
        if path.exists():
            # QPixmap accepts str; using str() avoids Windows backslash escape issues elsewhere
            self.original_pixmap = QPixmap(str(path))
            self.update_photo_label()
        else:
            self.original_pixmap = None
            self.photo_label.setText("❌ Could not load photo")

    def update_photo_label(self) -> None:
        if self.original_pixmap:
            scaled = self.original_pixmap.scaled(
                self.photo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.photo_label.setPixmap(scaled)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_photo_label()

    def handle_print_yes(self) -> None:
        if self.current_photo_path:
            print("🖨️ Printing photo...")
            ok = send_to_printer(str(self.current_photo_path))
            if not ok:
                print("⚠️ Print failed.")
        else:
            print("⚠️ No photo to print.")

    def handle_print_no(self) -> None:
        print("⏭️ Skipping print")
        self.hide_print_prompt()
        self.show_email_prompt()

    def hide_print_prompt(self) -> None:
        self.print_group.setVisible(False)

    def show_email_prompt(self) -> None:
        self.email_group.setVisible(True)

    def handle_email_yes(self) -> None:
        print("📧 Emailing photo...")
        to_email = "pcx.tony@gmail.com"  # TODO: replace with user input
        if self.current_photo_path:
            send_email(to_email, str(self.current_photo_path))
        self.controller.go_to(self.controller.idle_screen)

    def handle_email_no(self) -> None:
        print("❌ Skipping email")
        self.controller.go_to(self.controller.idle_screen)
