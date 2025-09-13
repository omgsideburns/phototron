from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
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
        self.layout.setSpacing(12)
        self.photo_label = QLabel("Photo will appear here")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Give the photo preview more space than controls
        self.layout.addWidget(self.photo_label,10)

        # Print group
        self.print_group = QWidget()
        print_layout = QVBoxLayout()
        print_layout.setContentsMargins(0, 0, 0, 0)
        print_layout.setSpacing(6)
        self.print_prompt = QLabel("What a great picture!")
        self.print_prompt.setAlignment(Qt.AlignCenter)

        self.print_yes_btn = QPushButton("Print My Picture!")
        self.print_yes_btn.setObjectName("YesButton")
        self.print_no_btn = QPushButton("Skip")
        self.print_no_btn.setObjectName("NoButton")
        self.print_yes_btn.clicked.connect(self.handle_print_yes)
        self.print_no_btn.clicked.connect(self.handle_print_no)

        self.print_prompt.setWordWrap(True)
        print_layout.addWidget(self.print_prompt)
        print_layout.addSpacing(16)
        print_layout.addWidget(self.print_yes_btn)
        print_layout.addWidget(self.print_no_btn)
        self.print_group.setLayout(print_layout)
        # Do not stretch control group; keep it compact
        self.layout.addWidget(self.print_group, 0)

        # Email group (hidden initially)
        self.email_group = QWidget()
        email_layout = QVBoxLayout()
        email_layout.setContentsMargins(0, 0, 0, 0)
        email_layout.setSpacing(6)
        self.email_prompt = QLabel("Where should we send your photos?")
        self.email_prompt.setAlignment(Qt.AlignCenter)
        # Input for recipient email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        self.email_yes_btn = QPushButton("Send it to me!")
        self.email_yes_btn.setObjectName("YesButton")
        self.email_no_btn = QPushButton("Skip")
        self.email_no_btn.setObjectName("NoButton")
        self.email_yes_btn.clicked.connect(self.handle_email_yes)
        self.email_no_btn.clicked.connect(self.handle_email_no)

        self.email_prompt.setWordWrap(True)
        email_layout.addWidget(self.email_prompt)
        email_layout.addWidget(self.email_input)
        email_layout.addWidget(self.email_yes_btn)
        email_layout.addWidget(self.email_no_btn)
        
        self.email_group.setLayout(email_layout)
        self.email_group.setVisible(False)
        self.layout.addWidget(self.email_group, 0)

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
        to_email = self.email_input.text().strip()
        if not to_email:
            print("⚠️ No email entered; skipping send.")
            return
        if self.current_photo_path:
            send_email(to_email, str(self.current_photo_path))
        self.controller.go_to(self.controller.idle_screen)

    def handle_email_no(self) -> None:
        print("❌ Skipping email")
        self.controller.go_to(self.controller.idle_screen)
