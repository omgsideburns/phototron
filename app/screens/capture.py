from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
import os
from datetime import datetime

class CaptureScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout()

        self.preview_label = QLabel("📸 [ Camera Preview Placeholder ]")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        take_photo_btn = QPushButton("Take Photo")
        take_photo_btn.setMinimumHeight(80)
        take_photo_btn.clicked.connect(self.take_photo)
        layout.addWidget(take_photo_btn)

        self.setLayout(layout)

    def take_photo(self):
        print("TAKE PHOTO pressed")
        session_path = self.controller.current_session_dir
        if not session_path:
            print("⚠️ No session selected.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        full_path = os.path.join(session_path, filename)

        try:
            self.controller.camera.start_camera()
            self.controller.camera.capture(full_path)
            print(f"✅ Photo saved to {full_path}")
            self.controller.preview_screen.load_photo(full_path)
            self.controller.go_to(self.controller.preview_screen)
        except Exception as e:
            print(f"❌ Capture failed: {e}")