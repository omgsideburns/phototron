from PySide6.QtWidgets import QApplication
from app.core import AppController
import sys

app = QApplication(sys.argv)

controller = AppController()
controller.widget().show()  # This shows the stack with IdleScreen already loaded

sys.exit(app.exec())

app = QApplication(sys.argv)
controller = AppController()
controller.widget().showFullScreen()
stack = QStackedWidget()
stack.addWidget(IdleScreen())
stack.showFullScreen()
sys.exit(app.exec())
