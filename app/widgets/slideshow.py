from pathlib import Path
import random

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PySide6.QtWidgets import QWidget, QLabel, QStackedLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap

from app.config import EVENT_COMPS, IDLE_CONFIG  # EVENT_COMPS should be a Path


class SlideshowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Config
        self.transition_time = IDLE_CONFIG.get("transition_time", 5000)   # ms
        self.transition_speed = IDLE_CONFIG.get("transition_speed", 5000) # ms
        self.transition_type = IDLE_CONFIG.get("transition_type", "fade")

        self.transitions = {
            "instant": self.instant_transition,
            "fade": self.fade_transition,
            "slide": self.slide_transition,
            "stack": self.stack_transition,
        }

        # Load image paths (JPGs in EVENT_COMPS)
        self.image_paths: list[Path] = sorted(Path(EVENT_COMPS).glob("*.jpg"))
        self.current_index = 0

        # Stack with two labels
        self.stack = QStackedLayout(self)
        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.stack.addWidget(self.label1)
        self.stack.addWidget(self.label2)
        self.setLayout(self.stack)

        for label in (self.label1, self.label2):
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(False)  # we’ll scale pixmaps ourselves
            label.setStyleSheet("background-color: black;")

        # Defer first load until we have a real size
        self._initialized = False
        self._first_transition_done = False
        self._target_w = 0
        self._target_h = 0

        # Timer (started on first show)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)

        # keep a reference to animations so they don't get GC'd
        self._anims: list[QPropertyAnimation] = []

    def refresh_images(self, shuffle: bool = True) -> None:
        base = Path(EVENT_COMPS)
        paths = sorted(base.glob("*.jpg"))
        if shuffle:
            random.shuffle(paths)
        self.image_paths = paths
        # Reset index and show first immediately if initialized
        self.current_index = 0 if self.image_paths else -1
        if self.image_paths:
            current_label = self.stack.currentWidget() or self.label1
            pm = QPixmap(str(self.image_paths[0]))
            current_label.setPixmap(self._scaled(pm, current_label))
            self.stack.setCurrentWidget(current_label)

    # ---- helpers ------------------------------------------------------------
    def _scaled(self, pixmap: QPixmap, label: QLabel) -> QPixmap:
        if pixmap.isNull():
            return pixmap
        # Use a stable target size to avoid first-frame artifacts
        w = self._target_w or label.width() or self.width()
        h = self._target_h or label.height() or self.height()
        if w <= 0 or h <= 0:
            return pixmap
        return pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def _init_first_frame(self):
        if self._initialized:
            return
        self._initialized = True
        if not self.image_paths:
            return
        # Establish stable target size now that layout has run
        self._target_w, self._target_h = max(1, self.width()), max(1, self.height())
        # Preload first (and second, if present) with correct scaling
        first_pm = QPixmap(str(self.image_paths[0]))
        self.label1.setPixmap(self._scaled(first_pm, self.label1))
        if len(self.image_paths) > 1:
            second_pm = QPixmap(str(self.image_paths[1]))
            self.label2.setPixmap(self._scaled(second_pm, self.label2))
        self.stack.setCurrentWidget(self.label1)
        # Start timer only after first frame is properly sized
        self.timer.start(self.transition_time)

    # ---- slideshow core -----------------------------------------------------
    def next_image(self):
        if not self.image_paths:
            return

        self.current_index = (self.current_index + 1) % len(self.image_paths)
        next_pm = QPixmap(str(self.image_paths[self.current_index]))

        current_label = self.stack.currentWidget()
        next_label = self.label1 if current_label is self.label2 else self.label2

        next_label.setPixmap(self._scaled(next_pm, next_label))
        self.stack.setCurrentWidget(next_label)

        # Force the very first transition to be instant to avoid odd first-time effects
        if not self._first_transition_done:
            self.instant_transition(next_label)
            self._first_transition_done = True
        else:
            transition_func = self.transitions.get(self.transition_type, self.instant_transition)
            transition_func(next_label)

    # ---- transitions --------------------------------------------------------
    def instant_transition(self, label: QLabel):
        label.setGraphicsEffect(None)

    def fade_transition(self, label: QLabel):
        effect = QGraphicsOpacityEffect(self)
        label.setGraphicsEffect(effect)
        effect.setOpacity(0.0)

        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(self.transition_speed)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()
        self._anims.append(anim)

    def slide_transition(self, label: QLabel):
        label.setGraphicsEffect(None)
        label.move(self.width(), 0)
        label.show()

        anim = QPropertyAnimation(label, b"pos", self)
        anim.setDuration(self.transition_speed)
        anim.setStartValue(QPoint(self.width(), 0))
        anim.setEndValue(QPoint(0, 0))
        anim.start()
        self._anims.append(anim)

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
        self._anims.append(anim)

    # ---- resize handling ----------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update stable target size and rescale
        if self.width() > 0 and self.height() > 0:
            self._target_w, self._target_h = self.width(), self.height()
        for label in (self.label1, self.label2):
            if label.pixmap():
                label.setPixmap(self._scaled(label.pixmap(), label))
        # If not yet initialized, do it as soon as we get a non-zero size
        if not self._initialized and self.width() > 0 and self.height() > 0:
            QTimer.singleShot(0, self._init_first_frame)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._initialized:
            QTimer.singleShot(0, self._init_first_frame)
