from pathlib import Path
import platform
import numpy as np

# Qt
from PySide6.QtGui import QImage, QColor

# Detect whether we’re on a Raspberry Pi.. only tested on a 5
ON_PI = platform.system() == "Linux" and "aarch64" in platform.machine()

if ON_PI:
    from picamera2 import Picamera2, Preview
    from libcamera import Transform, controls
else:
    Picamera2 = None
    Preview = None
    Transform = None
    controls = None


class CameraManager:
    def __init__(self, config=None):
        self.picam = None
        self.preview_started = False
        self.config = config or {}
        self._preview_config = None
        self._still_config = None

    def start_camera(self):
        if not ON_PI:
            print("Running in mock mode — camera not enabled.")
            return

        if self.picam is None:
            self.picam = Picamera2()
            resolution = tuple(self.config.get("resolution", [720, 1280]))
            # Preview transforms
            prev_hflip = bool(self.config.get("hflip", 0))
            prev_vflip = bool(self.config.get("vflip", 0))
            # Capture transforms (default to no flip unless explicitly set)
            cap_resolution = tuple(self.config.get("capture_resolution", resolution))
            cap_hflip = bool(self.config.get("capture_hflip", 0))
            cap_vflip = bool(self.config.get("capture_vflip", 0))

            self._preview_config = self.picam.create_preview_configuration(
                main={"size": resolution},
                transform=Transform(hflip=prev_hflip, vflip=prev_vflip),
            )
            self._still_config = self.picam.create_still_configuration(
                main={"size": cap_resolution},
                transform=Transform(hflip=cap_hflip, vflip=cap_vflip),
            )

            self.picam.configure(self._preview_config)
            self.picam.start_preview(Preview.NULL)
            self.picam.start()
            self.preview_started = True

            # Optional autofocus controls (Camera Module 3 / autofocus lenses)
            # Configure via [camera] in config: af_mode: auto|continuous|manual|off,
            # af_trigger_on_start: bool, lens_position: float (manual mode only)
            try:
                if controls is not None:
                    # AF Range: normal | macro | full (default normal)
                    rng = str(self.config.get("af_range", "normal")).lower()
                    try:
                        if rng == "macro":
                            self.picam.set_controls({"AfRange": controls.AfRangeEnum.Macro})
                        elif rng == "full":
                            self.picam.set_controls({"AfRange": controls.AfRangeEnum.Full})
                        else:
                            self.picam.set_controls({"AfRange": controls.AfRangeEnum.Normal})
                    except Exception:
                        pass

                    mode = str(self.config.get("af_mode", "auto")).lower()
                    if mode == "continuous":
                        self.picam.set_controls(
                            {"AfMode": controls.AfModeEnum.Continuous}
                        )
                    elif mode == "manual":
                        lp = float(self.config.get("lens_position", 5.0))
                        self.picam.set_controls(
                            {
                                "AfMode": controls.AfModeEnum.Manual,
                                "LensPosition": lp,
                            }
                        )
                    elif mode == "off":
                        # Some stacks have no explicit Off; Manual without LensPosition change is a reasonable hold.
                        self.picam.set_controls({"AfMode": controls.AfModeEnum.Manual})
                    else:  # "auto" (default)
                        self.picam.set_controls({"AfMode": controls.AfModeEnum.Auto})
                        if bool(self.config.get("af_trigger_on_start", True)):
                            self.picam.set_controls(
                                {"AfTrigger": controls.AfTrigger.Start}
                            )
            except Exception as e:
                print(f"⚠️ AF control setup skipped: {e}")

    def get_qt_preview_frame(self):
        if not ON_PI:
            # Return dummy frame (gray box) on macOS
            dummy = QImage(720, 1280, QImage.Format_RGB32)
            dummy.fill(QColor("darkgray"))
            return dummy

        if self.picam is None:
            return None

        try:
            arr = self.picam.capture_array("main")
            if arr is None:
                return None

            # Assume camera provides RGB or RGBA; do not swap channels
            if arr.ndim == 3 and arr.shape[2] >= 3:
                if arr.shape[2] == 3:
                    rgb = arr
                else:  # use first 4 channels if present
                    rgb = arr[:, :, :4]
            else:
                return None

            rgb = np.ascontiguousarray(rgb)
            h, w = rgb.shape[0], rgb.shape[1]
            if rgb.shape[2] == 4:
                return QImage(rgb.data, w, h, 4 * w, QImage.Format_RGBA8888)
            else:
                return QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        except Exception as e:
            print(f"⚠️ Preview frame error: {e}")
            return None

    def capture(self, filename):
        filepath = Path(filename).resolve()
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if not ON_PI:
            from PIL import Image, ImageDraw

            img = Image.new("RGB", (480, 640), color=(100, 100, 100))
            ImageDraw.Draw(img).text((10, 10), "Simulated Image", fill=(255, 255, 255))
            print(f"[capture] mock saved: {filepath}")
            img.save(filepath)
            return filepath

        if not self.preview_started:
            print("[capture] preview not started → start_camera()")
            self.start_camera()

        used_switch = False
        try:
            if self._still_config is not None:
                print("[capture] using STILL config → switch+capture:", filepath)
                used_switch = True
                self.picam.switch_mode_and_capture_file(self._still_config, filepath)
                print("[capture] still capture ok")
            else:
                print("[capture] no still config → capture in current mode:", filepath)
                self.picam.capture_file(filepath)
                print("[capture] preview-mode capture ok")
        except Exception as e:
            print(f"[capture] ERROR during capture: {e} → fallback capture_file")
            self.picam.capture_file(filepath)
        finally:
            # Only try to reconfigure if we DIDN'T use the switch helper.
            # When using switch_mode_and_capture_file, preview is already restored.
            if not used_switch and self._preview_config is not None:
                try:
                    self.picam.configure(self._preview_config)
                    print("[capture] preview restored")
                except Exception as e:
                    print(f"[capture] failed to restore preview: {e}")

        return filepath

    def close(self):
        if ON_PI and self.picam:
            self.picam.stop_preview()
            self.picam.close()
        self.picam = None
        self.preview_started = False
