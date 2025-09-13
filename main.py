import sys
from PySide6.QtWidgets import QApplication
from app.core import AppController

def choose_style():
    # Use the same base style across platforms
    return "Fusion"


def main():
    app = QApplication(sys.argv)
    app.setAutoSipEnabled

    # Set a safe style
    style = choose_style()
    if style:
        app.setStyle(style)

    controller = AppController()
    win = controller.widget()
    win.resize(480, 640)
    win.setFixedSize(480, 640)
    win.show()  # or win.showFullScreen()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
