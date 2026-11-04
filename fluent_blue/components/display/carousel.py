"""Carousel and Kbd."""
from __future__ import annotations

from ...compatibility.qt import (
    QEvent,
    QFontMetrics,
    QHBoxLayout,
    QPainter,
    QPen,
    QRectF,
    QSize,
    QSizePolicy,
    QStackedWidget,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.animations import fade
from ...core.theme_manager import ThemeManager
from ..base import ThemedMixin, check_choice
from ..buttons.button import IconButton


class _Dots(QWidget):
    """Page indicator. Each dot is a click target."""

    clicked = Signal(int)
    SPACING, DOT = 14, 8

    def __init__(self) -> None:
        super().__init__()
        self._count, self._current = 0, 0
        self.setFixedHeight(20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_state(self, count: int, current: int) -> None:
        self._count, self._current = count, current
        self.setFixedWidth(max(1, count * self.SPACING + 8))
        self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        index = int(event.position().x() // self.SPACING)
        if 0 <= index < self._count:
            self.clicked.emit(index)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        for index in range(self._count):
            active = index == self._current
            width = 18 if active else self.DOT
            x = 4 + index * self.SPACING + (0 if not active else -5)
            painter.setBrush(ThemeManager.qcolor("primary" if active else "border-strong"))
            painter.drawRoundedRect(QRectF(x, (self.height() - self.DOT) / 2, width, self.DOT), 4, 4)
        painter.end()


class Carousel(ThemedMixin, QWidget):
    """A set of slides shown one at a time, with arrows, dots, keyboard and optional autoplay.

    Autoplay pauses while the pointer is over the carousel, while it has keyboard focus, and while it is hidden.

    Args:
        autoplay_ms: Milliseconds between slides; 0 turns autoplay off.
        loop: Wrap from the last slide to the first and back.
        show_arrows: Show previous and next buttons.
        show_dots: Show the page indicator.

    Signals:
        current_changed(int): The index of the slide now shown.
    """

    current_changed = Signal(int)

    def __init__(self, parent=None, *, autoplay_ms: int = 0, loop: bool = True, show_arrows: bool = True, show_dots: bool = True) -> None:
        super().__init__(parent)
        self._loop = loop
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Carousel")
        column = QVBoxLayout(self)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(8)
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        column.addWidget(self.stack, 1)
        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.previous_button = IconButton("chevron-left", size="small", variant="secondary", tooltip="Previous slide")
        self.next_button = IconButton("chevron-right", size="small", variant="secondary", tooltip="Next slide")
        self.dots = _Dots()
        self.previous_button.clicked.connect(lambda: self.previous())
        self.next_button.clicked.connect(lambda: self.next())
        self.dots.clicked.connect(self.set_current)
        self.previous_button.setVisible(show_arrows)
        self.next_button.setVisible(show_arrows)
        self.dots.setVisible(show_dots)
        controls.addStretch(1)
        controls.addWidget(self.previous_button)
        controls.addWidget(self.dots)
        controls.addWidget(self.next_button)
        controls.addStretch(1)
        column.addLayout(controls)
        self._timer = QTimer(self)
        self._timer.setInterval(max(0, autoplay_ms) or 4000)
        self._timer.timeout.connect(self._advance)
        self._autoplay = autoplay_ms > 0
        self._paused = False
        self.bind_theme()
        self._sync()

    def add_slide(self, widget) -> int:
        """Add a slide and return its index."""
        index = self.stack.addWidget(widget)
        self._sync()
        return index

    def count(self) -> int:
        return self.stack.count()

    def current(self) -> int:
        return self.stack.currentIndex()

    def set_current(self, index: int) -> None:
        """Show a slide; out-of-range indexes are clamped, or wrapped when ``loop`` is on."""
        count = self.count()
        if count == 0:
            return
        index = index % count if self._loop else min(max(0, index), count - 1)
        if index == self.current():
            return
        self.stack.setCurrentIndex(index)
        if self.isVisible():
            fade(self.stack.currentWidget(), 0.0, 1.0, duration="normal")
        self._sync()
        self._timer.start() if self._should_play() else self._timer.stop()
        self.current_changed.emit(index)

    def next(self) -> None:
        self.set_current(self.current() + 1)

    def previous(self) -> None:
        self.set_current(self.current() - 1)

    def set_autoplay(self, milliseconds: int) -> None:
        """Change the autoplay interval; 0 stops autoplay."""
        self._autoplay = milliseconds > 0
        if self._autoplay:
            self._timer.setInterval(milliseconds)
        self._update_timer()

    def is_playing(self) -> bool:
        return self._timer.isActive()

    def _should_play(self) -> bool:
        return self._autoplay and not self._paused and self.isVisible() and self.count() > 1 and not self.hasFocus()

    def _update_timer(self) -> None:
        self._timer.start() if self._should_play() else self._timer.stop()

    def _advance(self) -> None:
        if not self._loop and self.current() >= self.count() - 1:
            self._timer.stop()
            return
        self.next()

    def _sync(self) -> None:
        count, current = self.count(), self.current()
        self.dots.set_state(count, max(0, current))
        self.previous_button.setEnabled(self._loop and count > 1 or current > 0)
        self.next_button.setEnabled(self._loop and count > 1 or current < count - 1)
        self.setAccessibleDescription(f"Slide {current + 1} of {count}" if count else "")

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() == Qt.Key.Key_Left:
            self.previous()
        elif event.key() == Qt.Key.Key_Right:
            self.next()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().showEvent(event)
        self._update_timer()

    def hideEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().hideEvent(event)
        self._timer.stop()

    def enterEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().enterEvent(event)
        self._paused = True
        self._timer.stop()

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().leaveEvent(event)
        self._paused = False
        self._update_timer()

    def focusInEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().focusInEvent(event)
        self._timer.stop()

    def focusOutEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().focusOutEvent(event)
        self._update_timer()

    def changeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._update_timer()


class Kbd(ThemedMixin, QWidget):
    """A keyboard shortcut drawn as key caps, such as ``Ctrl`` + ``K``.

    Args:
        keys: A string such as ``"Ctrl+Shift+P"``, or a list of key names.
        size: ``small`` or ``medium``.
    """

    SIZES = {"small": (11, 20), "medium": (12, 24)}

    def __init__(self, keys: str | list[str] = "", parent=None, *, size: str = "medium") -> None:
        super().__init__(parent)
        check_choice("size", size, self.SIZES)
        self._size = size
        self._keys: list[str] = []
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.bind_theme()
        self.set_keys(keys)

    def keys(self) -> list[str]:
        return list(self._keys)

    def set_keys(self, keys: str | list[str]) -> None:
        """Replace the keys. A string is split on ``+``; spaces around names are ignored."""
        parts = keys.split("+") if isinstance(keys, str) else keys
        self._keys = [part.strip() for part in parts if part and part.strip()]
        self.setAccessibleName("Keyboard shortcut " + " ".join(self._keys))
        self.updateGeometry()
        self.update()

    def _font(self):
        font = ThemeManager.font("label")
        font.setPixelSize(self.SIZES[self._size][0])
        return font

    def _cap_widths(self) -> list[int]:
        metrics = QFontMetrics(self._font())
        return [max(self.SIZES[self._size][1], metrics.horizontalAdvance(key) + 14) for key in self._keys]

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        gaps = max(0, len(self._keys) - 1) * 6
        return QSize(sum(self._cap_widths()) + gaps + 2, self.SIZES[self._size][1] + 3)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font())
        height = self.SIZES[self._size][1]
        x = 1.0
        for key, width in zip(self._keys, self._cap_widths()):
            cap = QRectF(x, 0.5, width, height)
            painter.setBrush(ThemeManager.qcolor("surface-secondary"))
            painter.setPen(QPen(ThemeManager.qcolor("border"), 1))
            painter.drawRoundedRect(cap, 5, 5)
            painter.setPen(QPen(ThemeManager.qcolor("border-strong"), 1.5))  # The bottom edge gives the key its depth.
            painter.drawLine(int(cap.left() + 4), int(cap.bottom() + 1), int(cap.right() - 4), int(cap.bottom() + 1))
            painter.setPen(ThemeManager.qcolor("text-secondary"))
            painter.drawText(cap, Qt.AlignmentFlag.AlignCenter, key)
            x += width + 6
        painter.end()
