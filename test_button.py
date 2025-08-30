from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animate Click Example")

        layout = QVBoxLayout()
        self.button = QPushButton("Click Me")
        self.button.clicked.connect(self.on_button_clicked)

        # Connect a separate button to trigger the animated click
        self.animate_button = QPushButton("Animate Click")
        self.animate_button.clicked.connect(self.button.animateClick)

        layout.addWidget(self.button)
        layout.addWidget(self.animate_button)
        self.setLayout(layout)

    def on_button_clicked(self):
        print("Button was clicked!")

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
