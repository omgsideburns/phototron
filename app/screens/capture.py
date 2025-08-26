from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
import os
from datetime import datetime
from app.collage import generate_collage

class CaptureScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.photo_index = 0
        self.photos_to_take = self.controller.config.get("photo", {}).get("count", 3)
        self.photo_paths = []

        self.layout = QVBoxLayout()

        self.preview_label = QLabel("📸 Camera Preview Starting...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.preview_label)

        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("font-size: 48px;")
        self.layout.addWidget(self.countdown_label)

        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)

        self.setLayout(self.layout)

    def start_sequence(self):
        self.photo_index = 0
        self.photo_paths = []
        self.preview_label.setText("📸 Warming up camera...")
        self.controller.camera.start_camera()
        self.preview_timer.start(50)  # ~20 FPS

        QTimer.singleShot(2000, self.begin_countdown)

    def update_preview(self):
        frame = self.controller.camera.get_qt_preview_frame()
        if frame:
            pixmap = QPixmap.fromImage(frame.scaled(800, 600, Qt.KeepAspectRatio))
            self.preview_label.setPixmap(pixmap)

    def begin_countdown(self):
        self.count = 3
        self.countdown_label.setText(str(self.count))
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.count -= 1
        if self.count > 0:
            self.countdown_label.setText(str(self.count))
        else:
            self.timer.stop()
            self.countdown_label.setText("📷")
            QTimer.singleShot(500, self.take_photo)

    def take_photo(self):
        session_path = self.controller.current_session_dir
        if not session_path:
            print("⚠️ No session selected.")
            return

        # NEW: Raw photo folder
        raw_dir = os.path.join(session_path, "raw")
        os.makedirs(raw_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_photo{self.photo_index + 1}.jpg"
        full_path = os.path.join(raw_dir, filename)

        try:
            self.controller.camera.capture(full_path)
            self.photo_paths.append(full_path)
            print(f"✅ Photo {self.photo_index + 1} saved to {full_path}")
        except Exception as e:
            print(f"❌ Capture failed: {e}")

        self.photo_index += 1
        if self.photo_index < self.photos_to_take:
            QTimer.singleShot(1000, self.begin_countdown)
        else:
            print("🎉 All photos captured.")

            self.preview_timer.stop()

            # NEW: Composite folder
            comps_dir = os.path.join(session_path, "comps")
            os.makedirs(comps_dir, exist_ok=True)
            composite_path = os.path.join(comps_dir, "composite.jpg")

            # Event-local logo file
            logo_path = os.path.join(session_path, self.controller.config['collage']['logo_filename'])

            generate_collage(
                self.photo_paths,
                composite_path,
                logo_path=logo_path,
                config=self.controller.config.get("collage", {})
            )
            
            self.controller.preview_screen.load_photo(composite_path)
            self.controller.go_to(self.controller.preview_screen)