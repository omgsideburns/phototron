import sys
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtCore import Qt
from app.config import APP_ROOT  # this is a Path object in your refactor
from app.core import AppController

def choose_style():
    # Prefer native on macOS, otherwise Fusion everywhere (including Windows/Linux)
    available = {s.lower(): s for s in QStyleFactory.keys()}
    if sys.platform == "darwin" and "macos" in available:
        return available["macos"]
    return available.get("fusion")

def main():
    app = QApplication(sys.argv)

    # Set a safe style
    style = choose_style()
    if style:
        app.setStyle(style)

    controller = AppController()
    win = controller.widget()
    win.resize(480, 640)
    win.show()  # or win.showFullScreen()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
