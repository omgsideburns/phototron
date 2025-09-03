from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtWidgets import QApplication
from app.config import APP_ROOT
from app.core import AppController
import os
import sys

os.chdir(APP_ROOT)

app = QApplication(sys.argv)
app.setStyle("macOS") # adding this forces macos to render more like the raspi does.. good for setting styles
controller = AppController()
controller.widget().resize(800, 600)
controller.widget().show()  # or .showFullScreen()
sys.exit(app.exec())

