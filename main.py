import os
import sys
import atexit
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale
from app import lights
from app.core import AppController

def choose_style():
    # Use the same base style across platforms
    return "Fusion"


def main():
    # Enable Qt Virtual Keyboard if available (install: qt6-virtualkeyboard)
    # Use default theme for broad availability and force US English layout.
    os.environ.setdefault("QT_IM_MODULE", "qtvirtualkeyboard")
    os.environ.setdefault("QT_VIRTUALKEYBOARD_STYLE", "default")
    os.environ.setdefault("QT_VIRTUALKEYBOARD_LANGUAGES", "en_US")
    # Also set the application locale to US English
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
    app = QApplication(sys.argv)
    # Ensure lights are turned off when the app exits
    try:
        app.aboutToQuit.connect(lights.shutdown)
        atexit.register(lights.shutdown)
    except Exception:
        pass
    app.setAutoSipEnabled

    # Set a safe style
    style = choose_style()
    if style:
        app.setStyle(style)

    controller = AppController()
    win = controller.widget()
    win.resize(480, 640)
    win.setFixedSize(480, 640)
    win.showFullScreen()  # or win.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
