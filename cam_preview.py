#!/usr/bin/env python3
"""
Standalone camera preview window using your app settings.

Run: python cam_preview.py

Controls:
- Esc or Q: Quit
- F: Toggle fullscreen

This uses CameraManager + [camera] settings from app/config.cfg (via user_config).
"""
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

from app.config import CAMERA_CONFIG
from app.camera import CameraManager


class CameraPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📷 Camera Preview — Esc to quit, F fullscreen")
        self.setMinimumSize(480, 640)

        self.camera = CameraManager(CAMERA_CONFIG)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel("Starting camera…")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.camera.start_camera()
        self.timer.start(50)  # ~20 FPS

    def update_frame(self):
        img = self.camera.get_qt_preview_frame()
        if img is None:
            return
        # Scale to fit while keeping aspect
        target = self.label.size()
        pm = QPixmap.fromImage(img).scaled(target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label.setPixmap(pm)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            QApplication.instance().quit()
            return
        if event.key() == Qt.Key_F:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        try:
            self.timer.stop()
        except Exception:
            pass
        try:
            self.camera.close()
        except Exception:
            pass
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    win = CameraPreview()
    win.resize(720, 1280)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

