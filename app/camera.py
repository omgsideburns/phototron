import os
from picamera2 import Picamera2, Preview
from libcamera import Transform
import time

class CameraManager:
    def __init__(self):
        self.picam = None
        self.preview_started = False
        self.config = config or {}

    def start_camera(self):
        if self.picam is None:
            self.picam = Picamera2()

            rotation = self.config.get("rotation", 0)
            resolution = tuple(self.config.get("resolution", [1280, 720]))

            config = self.picam.create_preview_configuration(
                main={"size": resolution},
                transform=Transform(rotation=rotation)
            )
            self.picam.configure(config)
            self.picam.start_preview(Preview.NULL)  # We’ll render to the GUI later
            self.picam.start()
            self.preview_started = True

    def capture(self, filename):
        if not self.preview_started:
            self.start_camera()
        filepath = os.path.abspath(filename)
        self.picam.capture_file(filepath)
        return filepath

    def close(self):
        if self.picam:
            self.picam.stop_preview()
            self.picam.close()
            self.picam = None
            self.preview_started = False