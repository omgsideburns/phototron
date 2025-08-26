from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class EmailScreen(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout()

        label = QLabel("📧 Email photo?")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        button_row = QHBoxLayout()
        yes_btn = QPushButton("Yes ✅")
        no_btn = QPushButton("No ❌")
        yes_btn.clicked.connect(self.email_yes)
        no_btn.clicked.connect(self.email_no)
        button_row.addWidget(yes_btn)
        button_row.addWidget(no_btn)

        layout.addLayout(button_row)
        self.setLayout(layout)

    def email_yes(self):
        print("📨 Email flow not implemented yet.")
        # TODO: Add actual email logic here
        self.controller.go_to(self.controller.idle_screen)

    def email_no(self):
        print("⏭️ Skipping email.")
        self.controller.go_to(self.controller.idle_screen)