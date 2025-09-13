from pathlib import Path
import re

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedLayout
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from app.collage import generate_collage
from app.config import PHOTO_CONFIG, EVENT_LOADED


class CaptureScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.photo_index = 0
        self.photo_paths: list[Path] = []
        self.photos_to_take = PHOTO_CONFIG.get("count", 3)
        self.countdown_seconds = PHOTO_CONFIG.get("countdown", 3)
        self.format = PHOTO_CONFIG.get("format", "jpg")
        self.quality = PHOTO_CONFIG.get("quality", 90)
        self.raw_subfolder = PHOTO_CONFIG.get("raw_path", "raw")
        self.comp_subfolder = PHOTO_CONFIG.get("composite_path", "comps")

        self.raw_dir: Path | None = None
        self.comps_dir: Path | None = None
        self.capture_session_id: str | None = None
        self.logo_path: Path | None = None

        # Layout with stacked overlay (preview + countdown overlay)
        layout = QVBoxLayout()

        self.preview_container = QWidget()
        self.preview_stack = QStackedLayout(self.preview_container)
        self.preview_stack.setStackingMode(QStackedLayout.StackAll)

        self.preview_label = QLabel("📸 Camera Preview Starting...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_stack.addWidget(self.preview_label)

        self.countdown_label = QLabel("")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.countdown_label.setObjectName("CountdownLabel")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(24)
        shadow.setColor(Qt.black)
        self.countdown_label.setGraphicsEffect(shadow)
        self.preview_stack.addWidget(self.countdown_label)

        # Track last preview pixmap for flash/restore
        self._last_preview_pixmap: QPixmap | None = None

        layout.addWidget(self.preview_container)
        self.setLayout(layout)

        # Timers
        self.preview_timer = QTimer(self)
        self.preview_timer.timeout.connect(self.update_preview)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

    def get_next_capture_session_id(self, raw_dir: Path) -> str:
        existing_files = [p.name for p in raw_dir.iterdir() if p.is_file()]
        session_numbers: list[int] = []

        for fname in existing_files:
            m = re.match(r"^(\d{4})-\d{2}\.\w+$", fname)
            if m:
                session_numbers.append(int(m.group(1)))

        next_id = (max(session_numbers) if session_numbers else 0) + 1
        return f"{next_id:04d}"


    # rewrite this to reference config paths... 
    def prepare_capture_paths(self) -> bool:
        session_path: Path = EVENT_LOADED
        if not session_path:
            print("⚠️ No event selected.")
            return False

        self.raw_dir = session_path / self.raw_subfolder
        self.raw_dir.mkdir(parents=True, exist_ok=True)

        self.comps_dir = session_path / self.comp_subfolder
        self.comps_dir.mkdir(parents=True, exist_ok=True)

        self.capture_session_id = self.get_next_capture_session_id(self.raw_dir)

        logo_filename = self.controller.config["collage"].get("logo_filename", "")
        self.logo_path = (session_path / logo_filename) if logo_filename else None

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
            # Scale live preview to ~75% of available area, keep aspect ratio
            cont_size = self.preview_container.size()
            target = QSize(max(1, int(cont_size.width() * 0.75)), max(1, int(cont_size.height() * 0.75)))
            scaled_img = frame.scaled(target, Qt.KeepAspectRatio, Qt.FastTransformation)
            pixmap = QPixmap.fromImage(scaled_img)
            self.preview_label.setPixmap(pixmap)
            self._last_preview_pixmap = pixmap

    def begin_countdown(self):
        # Ensure countdown label is on top of the stack
        if hasattr(self, "preview_stack"):
            self.preview_stack.setCurrentWidget(self.countdown_label)
        self.count = self.countdown_seconds
        self.countdown_label.setText(str(self.count))
        self.countdown_timer.start(1000)

    def update_countdown(self):
        self.count -= 1
        if self.count > 0:
            self.countdown_label.setText(str(self.count))
        else:
            self.countdown_timer.stop()
            self.countdown_label.setText("")
            # Ensure preview is the top widget
            self.preview_stack.setCurrentWidget(self.preview_label)
            # Flash only the preview area by swapping its pixmap to white
            if self._last_preview_pixmap is not None:
                size = self._last_preview_pixmap.size()
                white_img = QImage(size, QImage.Format_ARGB32)
                white_img.fill(Qt.white)
                white_pixmap = QPixmap.fromImage(white_img)
                # show white flash briefly
                self.preview_label.setPixmap(white_pixmap)
                QTimer.singleShot(150, lambda: self.preview_label.setPixmap(self._last_preview_pixmap))
                QTimer.singleShot(160, self.take_photo)
            else:
                # Fallback: just take photo if no preview yet
                self.take_photo()

    def take_photo(self):
        assert self.raw_dir is not None
        photo_num = self.photo_index + 1
        filename = f"{self.capture_session_id}-{photo_num:02d}.{self.format}"
        photo_path = self.raw_dir / filename

        try:
            # If your camera API expects a string, str() is safest:
            self.controller.camera.capture(str(photo_path))
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

            assert self.comps_dir is not None
            composite_path = self.comps_dir / f"{self.capture_session_id}-composite.jpg"

            generate_collage(
                self.photo_paths,  # list[Path]
                composite_path,  # Path
                logo_path=self.logo_path,  # Path | None
                config=self.controller.config.get("collage", {}),
            )

            # If preview_screen.load_photo expects a string, pass str()
            self.controller.preview_screen.load_photo(str(composite_path))
            self.controller.go_to(self.controller.preview_screen)
