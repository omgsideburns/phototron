from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox,
    QTextEdit, QComboBox, QPushButton, QMessageBox, QScrollArea, QFrame, QInputDialog
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt
from app.config import CONFIG, APP_ROOT, STYLE_ROOT, EVENT_BASE_PATH
from app.live_config import save_user_config
from functools import partial
import tomllib
import copy
import os
import sys


class SettingsScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Settings")
        self.widgets = {}

        main_layout = QVBoxLayout()

        # === Scrollable container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QFrame()
        layout = QVBoxLayout(content_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(QLabel("⚙️ Phototron Settings"))

        # === Load editable_keys.cfg
        with open(os.path.join(APP_ROOT, "app/editable_keys.cfg"), "rb") as f:
            editable = tomllib.load(f)

        for section, keys in editable.items():
            layout.addWidget(QLabel(f"[{section}]"))
            self.widgets[section] = {}

            for key, setting_type in keys.items():
                current_value = CONFIG.get(section, {}).get(key, "")
                label_text = key.replace("_", " ").title()
                widget = None

                # === Text input
                if setting_type == "text":
                    widget = QLineEdit(str(current_value))

                # === Number input
                elif setting_type == "number":
                    widget = QLineEdit(str(current_value))
                    widget.setValidator(QDoubleValidator())

                # === Boolean checkbox
                elif setting_type == "bool":
                    widget = QCheckBox(label_text)
                    widget.setChecked(bool(current_value))

                # === Select dropdown
                elif setting_type.startswith("select:"):
                    source = setting_type.split(":")[1]
                    widget = QComboBox()
                    options = []

                    if source == "styles":
                        if os.path.isdir(STYLE_ROOT):
                            options = sorted([
                                name for name in os.listdir(STYLE_ROOT)
                                if os.path.isdir(os.path.join(STYLE_ROOT, name))
                            ])
                        else:
                            print(f"⚠️ STYLE_ROOT missing: {STYLE_ROOT}")

                    elif source == "events":
                        if os.path.isdir(EVENT_BASE_PATH):
                            options = sorted([
                                name for name in os.listdir(EVENT_BASE_PATH)
                                if os.path.isdir(os.path.join(EVENT_BASE_PATH, name))
                            ])
                        else:
                            print(f"⚠️ EVENT_BASE_PATH missing: {EVENT_BASE_PATH}")

                    elif source == "email":
                        template_path = CONFIG.get("email", {}).get("template_path", "app/templates/email")
                        if os.path.isdir(template_path):
                            options = sorted([
                                name for name in os.listdir(template_path)
                                if name.endswith(".html")
                            ])

                    elif source == "flash_modes":
                        options = ["preview", "timed", "off"]

                    widget.addItems(options)
                    if current_value in options:
                        widget.setCurrentText(current_value)
                    elif options:
                        widget.setCurrentText(options[0])

                # === Add widgets
                if isinstance(widget, QCheckBox):
                    layout.addWidget(widget)
                else:
                    layout.addWidget(QLabel(f"{label_text}:"))
                    layout.addWidget(widget)

                self.widgets[section][key] = widget



                # === Add event folder creation
                if setting_type == "select:events":
                    add_btn = QPushButton("➕ Add Event")
                    layout.addWidget(add_btn)

                    def add_event():
                        new_name, ok = QInputDialog.getText(self, "Create New Event", "Event Name:")
                        if ok and new_name:
                            new_path = os.path.join(EVENT_BASE_PATH, new_name)
                            if not os.path.exists(new_path):
                                os.makedirs(new_path)
                                widget.addItem(new_name)
                                widget.setCurrentText(new_name)
                                QMessageBox.information(self, "Event Created", f"New event folder created:\n{new_name}")
                            else:
                                QMessageBox.warning(self, "Exists", "That event already exists.")

                    add_btn.clicked.connect(partial(self.add_event_folder, widget))

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # === Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("💾 Save + Restart")
        save_button.clicked.connect(self.save_and_restart)
        back_button = QPushButton("⬅️ Back")
        back_button.clicked.connect(self.go_back)

        button_layout.addWidget(save_button)
        button_layout.addWidget(back_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def add_event_folder(self, combo_widget):
        new_name, ok = QInputDialog.getText(self, "Create New Event", "Event Name:")
        if ok and new_name:
            new_path = os.path.join(EVENT_BASE_PATH, new_name)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                combo_widget.addItem(new_name)
                combo_widget.setCurrentText(new_name)
                QMessageBox.information(self, "Event Created", f"New event folder created:\n{new_name}")
            else:
                QMessageBox.warning(self, "Exists", "That event already exists.")

    def save_and_restart(self):
        from app.config import CONFIG as BASE_CONFIG
        merged_config = copy.deepcopy(BASE_CONFIG)

        for section, keys in self.widgets.items():
            if section not in merged_config:
                merged_config[section] = {}
            for key, widget in keys.items():
                if isinstance(widget, QLineEdit):
                    text = widget.text().strip()
                    try:
                        value = float(text)
                        merged_config[section][key] = value
                    except ValueError:
                        merged_config[section][key] = widget.text()
                elif isinstance(widget, QCheckBox):
                    merged_config[section][key] = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    merged_config[section][key] = widget.currentText()
                elif isinstance(widget, QTextEdit):
                    merged_config[section][key] = widget.toPlainText().strip()

        save_user_config(merged_config)
        QMessageBox.information(self, "Saved", "Settings saved. Phototron will now restart.")
        sys.exit(0)

    def go_back(self):
        self.controller.go_to(self.controller.idle_screen)