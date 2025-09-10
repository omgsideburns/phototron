from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PySide6.QtWidgets import QWidget, QLabel, QStackedLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap

from app.config import EVENT_COMPS, IDLE_CONFIG  # EVENT_COMPS is a Path


class SlideshowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Config
        self.transition_time = IDLE_CONFIG.get("transition_time", 5000)   # ms between slides
        self.transition_speed = IDLE_CONFIG.get("transition_speed", 500)  # ms animation duration
        self.transition_type = IDLE_CONFIG.get("transition_type", "fade")

        self.transitions = {
            "instant": self.instant_transition,
            "fade": self.fade_transition,
            "slide": self.slide_transition,
            "stack": self.stack_transition,
        }

        # Load image paths (jpg only; add more if needed)
        self.image_paths: list[Path] = sorted(EVENT_COMPS.glob("*.jpg"))
        self.current_index = 0

        # Stack with two labels (ping-pong)
        self.stack = QStackedLayout(self)
        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.stack.addWidget(self.label1)
        self.stack.addWidget(self.label2)
        self.setLayout(self.stack)

        for label in (self.label1, self.label2):
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(False)  # we scale pixmaps manually
            label.setStyleSheet("background-color: black;")

        # Start with first image
        if self.image_paths:
            pm = QPixmap(str(self.image_paths[0]))
            self.label1.setPixmap(self._scaled(pm, self.label1))

        # Timer to advance slides
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        self.timer.start(self.transition_time)

    # --- helpers -------------------------------------------------------------

    def _scaled(self, pixmap: QPixmap, label: QLabel) -> QPixmap:
        if pixmap.isNull() or label.width() <= 0 or label.height() <= 0:
            return pixmap
        return pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    # --- slideshow core ------------------------------------------------------

    def next_image(self):
        if not self.image_paths:
            return

        self.current_index = (self.current_index + 1) % len(self.image_paths)
        next_pm = QPixmap(str(self.image_paths[self.current_index]))

        current_label = self.stack.currentWidget()
        next_label = self.label1 if current_label is self.label2 else self.label2

        next_label.setPixmap(self._scaled(next_pm, next_label))
        self.stack.setCurrentWidget(next_label)

        # Run chosen transition
        transition_func = self.transitions.get(self.transition_type, self.instant_transition)
        transition_func(next_label)

    # --- transitions ---------------------------------------------------------

    def instant_transition(self, label: QLabel):
        label.setGraphicsEffect(None)

    def fade_transition(self, label: QLabel):
        effect = QGraphicsOpacityEffect(self)
        label.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        anim = QPropertyAnimation(effect, b"opacity", self)  # parent=self keeps it alive
        anim.setDuration(self.transition_speed)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()

    def slide_transition(self, label: QLabel):
        label.setGraphicsEffect(None)
        label.move(self.width(), 0)
        label.show()

        anim = QPropertyAnimation(label, b"pos", self)
        anim.setDuration(self.transition_speed)
        anim.setStartValue(QPoint(self.width(), 0))
        anim.setEndValue(QPoint(0, 0))
        anim.start()

    def stack_transition(self, label: QLabel):
        label.setGraphicsEffect(None)
        start_x = -self.width() // 4
        start_y = -self.height() // 4
        label.move(start_x, start_y)
        label.show()

        anim = QPropertyAnimation(label, b"pos", self)
        anim.setDuration(self.transition_speed)
        anim.setStartValue(QPoint(start_x, start_y))
        anim.setEndValue(QPoint(0, 0))
        anim.start()

    # --- resize handling -----------------------------------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)

        # Maintain 2:3 (width:height) → portrait frame
        container_w = self.width()
        container_h = self.height()
        target_ratio = 2 / 3

        if container_w / container_h > target_ratio:
            # Too wide — height limits
            label_h = container_h
            label_w = int(label_h * target_ratio)
        else:
            # Too tall — width limits
            label_w = container_w
            label_h = int(label_w / target_ratio)

        x = (container_w - label_w) // 2
        y = (container_h - label_h) // 2

        for label in (self.label1, self.label2):
            label.setGeometry(x, y, label_w, label_h)
            if label.pixmap():
                label.setPixmap(self._scaled(label.pixmap(), label))
