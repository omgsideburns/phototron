import os
import glob
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PySide6.QtWidgets import QWidget, QLabel, QStackedLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap

from app.config import EVENT_COMPS, IDLE_CONFIG


class SlideshowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Config
        self.transition_time = IDLE_CONFIG.get("transition_time", 5000)  # ms
        self.transition_speed = IDLE_CONFIG.get("transition_speed", 5000)
        self.transition_type = IDLE_CONFIG.get("transition_type", "fade")

        self.transitions = {
            "instant": self.instant_transition,
            "fade": self.fade_transition,
            "slide": self.slide_transition,
            "stack": self.stack_transition,
        }

        # Load image paths
        self.image_paths = sorted(glob.glob(os.path.join(EVENT_COMPS, "*.jpg")))
        self.current_index = 0

        # set up the stack...
        self.stack = QStackedLayout(self)
        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.stack.addWidget(self.label1)
        self.stack.addWidget(self.label2)
        self.setLayout(self.stack)

        for label in (self.label1, self.label2):
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(True)  # Important: allow QLabel to scale image inside
            label.setStyleSheet("background-color: black;")  # Optional visual anchor

        # Start with first image
        if self.image_paths:
            first_pixmap = QPixmap(self.image_paths[0])
            scaled = first_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label1.setPixmap(scaled)

        # Set up timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_image)
        self.timer.start(self.transition_time)

        self.fade = QPropertyAnimation(self.label2, b"windowOpacity")
        self.fade.setDuration(self.transition_speed)

    def next_image(self):
        if not self.image_paths:
            return

        self.current_index = (self.current_index + 1) % len(self.image_paths)
        next_pixmap = QPixmap(self.image_paths[self.current_index])

        current_label = self.stack.currentWidget()
        next_label = self.label1 if current_label is self.label2 else self.label2

        next_label.setPixmap(next_pixmap)

        self.stack.setCurrentWidget(next_label)

        # Dispatch transition by type
        transition_func = self.transitions.get(self.transition_type, self.instant_transition)
        transition_func(next_label)

    def instant_transition(self, label):
        label.setGraphicsEffect(None)

    def fade_transition(self, label):
        effect = QGraphicsOpacityEffect()
        label.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(self.transition_speed)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.start()

    def slide_transition(self, label):
        # Set initial position to the right of the widget
        label.setGraphicsEffect(None)
        label.move(self.width(), 0)
        label.show()

        animation = QPropertyAnimation(label, b"pos", self)
        animation.setDuration(self.transition_speed)
        animation.setStartValue(QPoint(self.width(), 0))
        animation.setEndValue(QPoint(0, 0))
        animation.start()

    def stack_transition(self, label):
        label.setGraphicsEffect(None)

        # Start offscreen top-left
        start_x = -self.width() // 4
        start_y = -self.height() // 4
        end_pos = QPoint(0, 0)

        label.move(start_x, start_y)
        label.show()

        animation = QPropertyAnimation(label, b"pos", self)
        animation.setDuration(self.transition_speed)
        animation.setStartValue(QPoint(start_x, start_y))
        animation.setEndValue(end_pos)
        animation.start()