from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class CaptureScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout()

        self.preview_label = QLabel("📸 [ Camera Preview Placeholder ]")
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        take_photo_btn = QPushButton("Take Photo")
        take_photo_btn.setMinimumHeight(80)
        take_photo_btn.clicked.connect(self.take_photo)
        layout.addWidget(take_photo_btn)

        self.setLayout(layout)

    def take_photo(self):
        print("TAKE PHOTO!")
        # Placeholder: go to preview screen later