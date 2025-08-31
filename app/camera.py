import os
import platform
import time
import numpy as np

# Qt
from PySide6.QtGui import QImage, QColor
from PySide6.QtCore import Qt

# Detect whether we’re on a Raspberry Pi.. only tested on a 5 
ON_PI = platform.system() == "Linux" and "aarch64" in platform.machine()

if ON_PI:
    from picamera2 import Picamera2, Preview
    from libcamera import Transform
else:
    Picamera2 = None
    Preview = None
    Transform = None


class CameraManager:
    def __init__(self, config=None):
        self.picam = None
        self.preview_started = False
        self.config = config or {}

    def start_camera(self):
        if not ON_PI:
            print("Running in mock mode — camera not enabled.")
            return

        if self.picam is None:
            self.picam = Picamera2()
            rotation = self.config.get("rotation", 0)
            resolution = tuple(self.config.get("resolution", [1280, 720]))

            config = self.picam.create_preview_configuration(
                main={"size": resolution},
                transform=Transform(rotation=rotation)
            )
            self.picam.configure(config)
            self.picam.start_preview(Preview.NULL)
            self.picam.start()
            self.preview_started = True

    def get_qt_preview_frame(self):
        if not ON_PI:
            # Return dummy frame (gray box) on macOS
            dummy = QImage(640, 480, QImage.Format_RGB32)
            dummy.fill(QColor("darkgray"))
            return dummy

        if self.picam is None:
            return None

        try:
            frame = self.picam.capture_array("main")
            if frame is None:
                return None

            # Don't call ascontiguousarray yet — do it after reordering
            if frame.shape[2] == 3:
                # Convert BGR to RGB
                frame = frame[:, :, ::-1]
                frame = np.ascontiguousarray(frame)
                height, width, _ = frame.shape
                bytes_per_line = 3 * width
                return QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            elif frame.shape[2] == 4:
                # Convert BGRA to RGBA
                frame = frame[:, :, [2, 1, 0, 3]]
                frame = np.ascontiguousarray(frame)
                height, width, _ = frame.shape
                bytes_per_line = 4 * width
                return QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGBA8888)

            else:
                print(f"⚠️ Unsupported channel count: {frame.shape[2]}")
                return None
        except Exception as e:
            print(f"⚠️ Preview frame error: {e}")
            return None

    def capture(self, filename):
        if not ON_PI:
            # Simulate camera capture on macOS
            from PIL import Image, ImageDraw
            img = Image.new("RGB", (640, 480), color=(100, 100, 100))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), "Simulated Image", fill=(255, 255, 255))
            filepath = os.path.abspath(filename)
            img.save(filepath)
            print(f"📸 Simulated photo saved to {filepath}")
            return filepath

        if not self.preview_started:
            self.start_camera()

        filepath = os.path.abspath(filename)
        self.picam.capture_file(filepath)
        return filepath

    def close(self):
        if ON_PI and self.picam:
            self.picam.stop_preview()
            self.picam.close()
        self.picam = None
        self.preview_started = False