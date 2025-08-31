from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from datetime import datetime
import os
import re

from app.collage import generate_collage
from app.config import PHOTO_CONFIG

class CaptureScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.photo_index = 0
        self.photo_paths = []
        self.photos_to_take = PHOTO_CONFIG.get("count", 3)
        self.countdown_seconds = PHOTO_CONFIG.get("countdown", 3)
        self.format = PHOTO_CONFIG.get("format", "jpg")
        self.quality = PHOTO_CONFIG.get("quality", 90)
        self.raw_subfolder = PHOTO_CONFIG.get("raw_path", "raw")
        self.comp_subfolder = PHOTO_CONFIG.get("composite_path", "comps")

        self.raw_dir = None
        self.comps_dir = None
        self.capture_session_id = None
        self.logo_path = None

        # Layout
        layout = QVBoxLayout()

        self.preview_label = QLabel("📸 Camera Preview Starting...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.countdown_label)

        self.setLayout(layout)

        # Timers
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.update_preview)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

    def get_next_capture_session_id(self, raw_dir):
        existing_files = os.listdir(raw_dir)
        session_numbers = []

        for fname in existing_files:
            match = re.match(r"^(\d{4})-\d{2}\.\w+$", fname)
            if match:
                session_numbers.append(int(match.group(1)))

        next_id = max(session_numbers, default=0) + 1
        return f"{next_id:04d}"

    def prepare_capture_paths(self):
        session_path = self.controller.current_session_dir
        if not session_path:
            print("⚠️ No session selected.")
            return False

        self.raw_dir = os.path.join(session_path, self.raw_subfolder)
        os.makedirs(self.raw_dir, exist_ok=True)

        self.comps_dir = os.path.join(session_path, self.comp_subfolder)
        os.makedirs(self.comps_dir, exist_ok=True)

        self.capture_session_id = self.get_next_capture_session_id(self.raw_dir)

        self.logo_path = os.path.join(
            session_path, self.controller.config["collage"]["logo_filename"]
        )

        print(f"📁 Prepared session {self.capture_session_id}")
        print("Raw path:", self.raw_dir)
        print("Comps path:", self.comps_dir)
        print("Logo path:", self.logo_path)
        return True

    def start_sequence(self):
        self.photo_index = 0
        self.photo_paths = []
        self.preview_label.setText("📸 Warming up camera...")

        if not self.prepare_capture_paths():
            return

        self.controller.camera.start_camera()
        self.preview_timer.start(50)  # ~20 FPS

        QTimer.singleShot(2000, self.begin_countdown)

    def update_preview(self):
        frame = self.controller.camera.get_qt_preview_frame()
        if frame:
            pixmap = QPixmap.fromImage(frame.scaled(800, 600, Qt.KeepAspectRatio))
            self.preview_label.setPixmap(pixmap)

    def begin_countdown(self):
        self.count = self.countdown_seconds
        self.countdown_label.setText(str(self.count))
        self.countdown_timer.start(1000)

    def update_countdown(self):
        self.count -= 1
        if self.count > 0:
            self.countdown_label.setText(str(self.count))
        else:
            self.countdown_timer.stop()
            self.countdown_label.setText("📷")
            QTimer.singleShot(500, self.take_photo)

    def take_photo(self):
        photo_num = self.photo_index + 1
        filename = f"{self.capture_session_id}-{photo_num:02d}.{self.format}"
        photo_path = os.path.join(self.raw_dir, filename)

        try:
            self.controller.camera.capture(photo_path)
            self.photo_paths.append(photo_path)
            print(f"✅ Photo {photo_num} saved to {photo_path}")
        except Exception as e:
            print(f"❌ Capture failed: {e}")

        self.photo_index += 1
        if self.photo_index < self.photos_to_take:
            QTimer.singleShot(1000, self.begin_countdown)
        else:
            print("🎉 All photos captured.")
            self.preview_timer.stop()

            composite_path = os.path.join(self.comps_dir, f"{self.capture_session_id}-composite.jpg")

            generate_collage(
                self.photo_paths,
                composite_path,
                logo_path=self.logo_path,
                config=self.controller.config.get("collage", {})
            )

            self.controller.preview_screen.load_photo(composite_path)
            self.controller.go_to(self.controller.preview_screen)