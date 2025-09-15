from pathlib import Path
import threading

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
)
from PySide6.QtGui import QPixmap, QGuiApplication
from PySide6.QtCore import Qt, QTimer

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
        self.print_prompt.setObjectName("PreviewPrompt")
        self.print_prompt.setAlignment(Qt.AlignCenter)

        self.print_yes_btn = QPushButton("Print My Picture!")
        self.print_yes_btn.setObjectName("YesButton")
        self.print_no_btn = QPushButton("Skip")
        self.print_no_btn.setObjectName("NoButton")
        self.print_yes_btn.clicked.connect(self.handle_print_yes)
        self.print_no_btn.clicked.connect(self.handle_print_no)

        # Status label to temporarily replace buttons after printing
        self.print_status = QLabel("Your picture is being printed...")
        self.print_status.setObjectName("PreviewStatus")
        self.print_status.setAlignment(Qt.AlignCenter)
        self.print_status.setVisible(False)

        self.print_prompt.setWordWrap(True)
        print_layout.addWidget(self.print_prompt)
        print_layout.addSpacing(16)
        print_layout.addWidget(self.print_yes_btn)
        print_layout.addWidget(self.print_no_btn)
        print_layout.addWidget(self.print_status)
        self.print_group.setLayout(print_layout)
        # Do not stretch control group; keep it compact
        self.layout.addWidget(self.print_group, 0)

        # Email group (hidden initially)
        self.email_group = QWidget()
        email_layout = QVBoxLayout()
        email_layout.setContentsMargins(0, 0, 0, 0)
        email_layout.setSpacing(6)
        self.email_prompt = QLabel("Where should we send your photos?")
        self.email_prompt.setObjectName("PreviewPrompt")
        self.email_prompt.setAlignment(Qt.AlignCenter)
        # Input for recipient email
        self.email_input = QLineEdit()
        self.email_input.setObjectName("EmailInput")
        self.email_input.setAlignment(Qt.AlignCenter)
        self.email_input.setPlaceholderText("Enter email address - We won't send any other emails!")
        self.email_input.setInputMethodHints(
            Qt.ImhEmailCharactersOnly | Qt.ImhNoPredictiveText | Qt.ImhPreferLowercase
        )
        self.email_input.textEdited.connect(self._clear_email_error)
        # Validation error label (hidden until invalid)
        self.email_error = QLabel("")
        self.email_error.setObjectName("PreviewError")
        self.email_error.setAlignment(Qt.AlignCenter)
        self.email_error.setVisible(False)
        # Optional on-screen keyboard toggle (helps if VK doesn't auto-show)
        self.keyboard_btn = QPushButton("Keyboard")
        self.keyboard_btn.setObjectName("YesButton")
        self.keyboard_btn.clicked.connect(self._show_virtual_keyboard)

        self.email_yes_btn = QPushButton("Send it to me!")
        self.email_yes_btn.setObjectName("YesButton")
        self.email_no_btn = QPushButton("Skip")
        self.email_no_btn.setObjectName("NoButton")
        self.email_yes_btn.clicked.connect(self.handle_email_yes)
        self.email_no_btn.clicked.connect(self.handle_email_no)

        # Status label to temporarily replace buttons after email send
        self.email_status = QLabel("Sending your photo...")
        self.email_status.setObjectName("PreviewStatus")
        self.email_status.setAlignment(Qt.AlignCenter)
        self.email_status.setVisible(False)

        self.email_prompt.setWordWrap(True)
        email_layout.addWidget(self.email_prompt)
        email_layout.addWidget(self.email_input)
        email_layout.addWidget(self.keyboard_btn)
        email_layout.addWidget(self.email_error)
        email_layout.addWidget(self.email_yes_btn)
        email_layout.addWidget(self.email_no_btn)
        email_layout.addWidget(self.email_status)
        
        self.email_group.setLayout(email_layout)
        self.email_group.setVisible(False)
        self.layout.addWidget(self.email_group, 0)

        self.setLayout(self.layout)
        # Spacer used to lift content above on-screen keyboard when visible
        self.keyboard_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addItem(self.keyboard_spacer)

        # Track virtual keyboard visibility/height to avoid covering inputs
        try:
            im = QGuiApplication.inputMethod()
            im.visibleChanged.connect(self._on_im_changed)
            im.keyboardRectangleChanged.connect(self._on_im_changed)
        except Exception:
            pass

    def load_photo(self, filepath: str | Path) -> None:
        path = Path(filepath)
        self.current_photo_path = path
        if path.exists():
            # QPixmap accepts str; using str() avoids Windows backslash escape issues elsewhere
            self.original_pixmap = QPixmap(str(path))
            self.update_photo_label()
            # Reset UI for new session
            self.print_group.setVisible(True)
            self.print_yes_btn.setVisible(True)
            self.print_no_btn.setVisible(True)
            self.print_status.setVisible(False)
            self.email_group.setVisible(False)
            self.email_yes_btn.setVisible(True)
            self.email_no_btn.setVisible(True)
            self.email_status.setVisible(False)
        else:
            self.original_pixmap = None
            self.photo_label.setText("Could not load photo")

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
        # Immediately show printing status and disable buttons to avoid lag/multiple clicks
        self.print_yes_btn.setVisible(False)
        self.print_no_btn.setVisible(False)
        self.print_status.setVisible(True)
        if self.current_photo_path:
            def _do_print():
                try:
                    ok = send_to_printer(str(self.current_photo_path))
                    if not ok:
                        print("Print failed.")
                except Exception as e:
                    print(f"Print error: {e}")
            threading.Thread(target=_do_print, daemon=True).start()
        else:
            print("No photo to print.")
        QTimer.singleShot(2000, self._after_print)

    def handle_print_no(self) -> None:
        print("Skipping print")
        self.hide_print_prompt()
        self.show_email_prompt()

    def hide_print_prompt(self) -> None:
        self.print_group.setVisible(False)

    def show_email_prompt(self) -> None:
        # Reset visibility for email prompt
        self.email_yes_btn.setVisible(True)
        self.email_no_btn.setVisible(True)
        self.email_status.setVisible(False)
        self.email_group.setVisible(True)
        # Focus input so VK shows and adjust layout above keyboard
        self.email_input.setFocus()
        self._adjust_for_keyboard()

    def _after_print(self) -> None:
        self.print_status.setVisible(False)
        self.hide_print_prompt()
        self.show_email_prompt()

    def handle_email_yes(self) -> None:
        print("Emailing photo...")
        to_email = self.email_input.text().strip()
        if not to_email or not self._is_valid_email(to_email):
            self.email_error.setText("Please enter a valid email address.")
            self.email_error.setVisible(True)
            self.email_input.setProperty("invalid", True)
            self.email_input.style().unpolish(self.email_input)
            self.email_input.style().polish(self.email_input)
            self.email_input.update()
            return
        # Immediately show sending state and disable buttons
        self.email_yes_btn.setVisible(False)
        self.email_no_btn.setVisible(False)
        self.email_status.setVisible(True)
        QTimer.singleShot(2000, lambda: self.controller.go_to(self.controller.idle_screen))
        # Send in background to avoid UI lag
        if self.current_photo_path:
            def _do_send():
                try:
                    send_email(to_email, str(self.current_photo_path))
                except Exception as e:
                    print(f"Email error: {e}")
            threading.Thread(target=_do_send, daemon=True).start()
        QTimer.singleShot(2000, lambda: self.controller.go_to(self.controller.idle_screen))

    def _is_valid_email(self, email: str) -> bool:
        # Simple, pragmatic email validation
        import re
        pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        return bool(re.match(pattern, email)) and len(email) <= 254

    def _clear_email_error(self, _text: str) -> None:
        if self.email_input.property("invalid"):
            self.email_input.setProperty("invalid", False)
            self.email_input.style().unpolish(self.email_input)
            self.email_input.style().polish(self.email_input)
            self.email_input.update()
        if self.email_error.isVisible():
            self.email_error.setVisible(False)

    def _show_virtual_keyboard(self) -> None:
        # Focus the input and ask Qt's input method (virtual keyboard) to show
        self.email_input.setFocus()
        try:
            QGuiApplication.inputMethod().show()
        except Exception:
            pass

    def _on_im_changed(self) -> None:
        self._adjust_for_keyboard()

    def _adjust_for_keyboard(self) -> None:
        try:
            im = QGuiApplication.inputMethod()
            rect = im.keyboardRectangle()
            visible = im.isVisible()
            h = int(rect.height()) if visible else 0
        except Exception:
            h = 0
        # Apply spacer height and relayout
        self.keyboard_spacer.changeSize(0, max(0, h), QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.invalidate()

    

    def handle_email_no(self) -> None:
        print("Skipping email")
        self.controller.go_to(self.controller.idle_screen)
