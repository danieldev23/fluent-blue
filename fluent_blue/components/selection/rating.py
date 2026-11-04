"""Rating and RangeSlider: two custom-painted, keyboard-operable value controls."""
from __future__ import annotations

from ...compatibility.qt import QPainter, QPainterPath, QPen, QPointF, QRectF, QSize, QSizePolicy, Qt, QWidget, Signal
from ...core.theme_manager import ThemeManager
from ..base import ThemedMixin, apply_common


def _star_path(center: QPointF, radius: float) -> QPainterPath:
    """A five-point star with a rounded look: inner radius 0.46 of the outer one."""
    import math

    path = QPainterPath()
    for index in range(10):
        angle = -math.pi / 2 + index * math.pi / 5
        r = radius if index % 2 == 0 else radius * 0.46
        point = QPointF(center.x() + r * math.cos(angle), center.y() + r * math.sin(angle))
        path.moveTo(point) if index == 0 else path.lineTo(point)
    path.closeSubpath()
    return path


class Rating(ThemedMixin, QWidget):
    """A star rating that can be set with the mouse or the keyboard.

    Left and Down lower the value, Right and Up raise it, Home clears it and End gives the maximum.

    Args:
        value: Initial value from 0 to ``count``.
        count: Number of stars.
        allow_half: Allow half-star values.
        allow_clear: Clicking the current value again resets it to 0.
        read_only: Display only; the value cannot be changed by the user.
        size: Star size in pixels.
        disabled: Start disabled.
        tooltip: Tooltip text.

    Signals:
        value_changed(float): The new value, after a change by the user or by ``set_value``.
    """

    value_changed = Signal(float)
    GAP = 4

    def __init__(self, value: float = 0, parent=None, *, count: int = 5, allow_half: bool = False, allow_clear: bool = True,
                 read_only: bool = False, size: int = 22, disabled: bool = False, tooltip: str | None = None) -> None:
        super().__init__(parent)
        self._count, self._half, self._clear, self._read_only, self._size = max(1, count), allow_half, allow_clear, read_only, size
        self._value = 0.0
        self._hover: float | None = None
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus if read_only else Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor if read_only else Qt.CursorShape.PointingHandCursor)
        self.bind_theme()
        apply_common(self, disabled=disabled, tooltip=tooltip, accessible_name="Rating")
        self.set_value(value)

    def value(self) -> float:
        return self._value

    def count(self) -> int:
        return self._count

    def step(self) -> float:
        return 0.5 if self._half else 1.0

    def set_value(self, value: float) -> None:
        """Set the value, clamped and snapped to the step. Emits ``value_changed`` if it changed."""
        step = self.step()
        value = round(min(max(float(value), 0.0), float(self._count)) / step) * step
        self.setAccessibleDescription(f"{value:g} of {self._count}")
        if value != self._value:
            self._value = value
            self.update()
            self.value_changed.emit(value)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(self._count * self._size + (self._count - 1) * self.GAP + 4, self._size + 4)

    def _value_at(self, x: float) -> float:
        cell = self._size + self.GAP
        index = min(self._count - 1, max(0, int((x - 2) // cell)))
        fraction = ((x - 2) - index * cell) / self._size
        return index + (0.5 if self._half and fraction < 0.5 else 1.0)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        if not self._read_only:
            self._hover = self._value_at(event.position().x())
            self.update()

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().leaveEvent(event)
        self._hover = None
        self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._read_only or event.button() != Qt.MouseButton.LeftButton:
            return
        chosen = self._value_at(event.position().x())
        self.set_value(0 if self._clear and chosen == self._value else chosen)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        key = event.key()
        if self._read_only:
            return super().keyPressEvent(event)
        if key in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            self.set_value(self._value - self.step())
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            self.set_value(self._value + self.step())
        elif key == Qt.Key.Key_Home:
            self.set_value(0)
        elif key == Qt.Key.Key_End:
            self.set_value(self._count)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shown = self._hover if self._hover is not None else self._value
        enabled = self.isEnabled()
        fill = ThemeManager.qcolor("warning" if enabled else "border-strong")
        outline = ThemeManager.qcolor("border-strong" if enabled else "border")
        radius = self._size / 2 - 1
        for index in range(self._count):
            left = 2 + index * (self._size + self.GAP)
            center = QPointF(left + self._size / 2, self.height() / 2)
            star = _star_path(center, radius)
            painter.setPen(QPen(outline, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(star)
            portion = min(1.0, max(0.0, shown - index))
            if portion > 0:
                painter.save()
                painter.setClipRect(QRectF(left, 0, self._size * portion, self.height()))
                painter.setPen(QPen(fill, 1.4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                painter.setBrush(fill)
                painter.drawPath(star)
                painter.restore()
        if self.hasFocus():
            painter.setPen(QPen(ThemeManager.qcolor("border-focus"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 4, 4)
        painter.end()


class RangeSlider(ThemedMixin, QWidget):
    """A slider with two handles that selects a range.

    Drag a handle, or click the track to move the nearer one. With the keyboard, Left and Right move the
    active handle, Down selects the lower handle and Up the upper one, and Home and End jump to a limit.

    Args:
        low: Initial lower value.
        high: Initial upper value.
        minimum: Lowest allowed value.
        maximum: Highest allowed value.
        step: Granularity of values.
        disabled: Start disabled.
        tooltip: Tooltip text.

    Signals:
        range_changed(int, int): The new lower and upper values.
    """

    range_changed = Signal(int, int)
    HANDLE = 16

    def __init__(self, low: int = 20, high: int = 80, parent=None, *, minimum: int = 0, maximum: int = 100, step: int = 1,
                 disabled: bool = False, tooltip: str | None = None) -> None:
        super().__init__(parent)
        if maximum <= minimum:
            raise ValueError("maximum must be greater than minimum.")
        self._min, self._max, self._step = minimum, maximum, max(1, step)
        self._low, self._high = minimum, maximum
        self._active = "high"
        self.setFixedHeight(28)
        self.setMinimumWidth(120)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bind_theme()
        apply_common(self, disabled=disabled, tooltip=tooltip, accessible_name="Range")
        self.set_range(low, high)

    def low(self) -> int:
        return self._low

    def high(self) -> int:
        return self._high

    def set_range(self, low: int, high: int) -> None:
        """Set both values, clamped, snapped and ordered. Emits ``range_changed`` if either changed."""
        low, high = self._snap(low), self._snap(high)
        low, high = min(low, high), max(low, high)
        self.setAccessibleDescription(f"{low} to {high}")
        if (low, high) != (self._low, self._high):
            self._low, self._high = low, high
            self.update()
            self.range_changed.emit(low, high)

    def _snap(self, value: float) -> int:
        value = min(max(value, self._min), self._max)
        return int(self._min + round((value - self._min) / self._step) * self._step)

    def _x(self, value: int) -> float:
        usable = self.width() - self.HANDLE
        return self.HANDLE / 2 + usable * (value - self._min) / (self._max - self._min)

    def _value_at(self, x: float) -> int:
        usable = max(1, self.width() - self.HANDLE)
        return self._snap(self._min + (x - self.HANDLE / 2) / usable * (self._max - self._min))

    def _move(self, x: float, choose: bool = False) -> None:
        value = self._value_at(x)
        if choose:
            self._active = "low" if abs(value - self._low) < abs(value - self._high) or (value <= self._low) else "high"
        if self._active == "low":
            self.set_range(min(value, self._high), self._high)
        else:
            self.set_range(self._low, max(value, self._low))

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        self.setFocus()
        self._move(event.position().x(), choose=True)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._move(event.position().x())

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        key = event.key()
        delta = {Qt.Key.Key_Left: -self._step, Qt.Key.Key_Right: self._step}.get(key)
        if key == Qt.Key.Key_Up:
            self._active = "high"
        elif key == Qt.Key.Key_Down:
            self._active = "low"
        elif key == Qt.Key.Key_Home:
            self.set_range(self._min, self._high) if self._active == "low" else self.set_range(self._low, self._low)
        elif key == Qt.Key.Key_End:
            self.set_range(self._high, self._max) if self._active == "low" else self.set_range(self._low, self._max)
        elif delta is not None:
            if self._active == "low":
                self.set_range(min(self._low + delta, self._high), self._high)
            else:
                self.set_range(self._low, max(self._high + delta, self._low))
        else:
            return super().keyPressEvent(event)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(240, 28)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        enabled = self.isEnabled()
        mid = self.height() / 2
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor("surface-tertiary"))
        painter.drawRoundedRect(QRectF(self.HANDLE / 2, mid - 2, self.width() - self.HANDLE, 4), 2, 2)
        x1, x2 = self._x(self._low), self._x(self._high)
        painter.setBrush(ThemeManager.qcolor("primary" if enabled else "border-strong"))
        painter.drawRoundedRect(QRectF(x1, mid - 2, max(0.0, x2 - x1), 4), 2, 2)
        for name, x in (("low", x1), ("high", x2)):
            ring = ThemeManager.qcolor("primary" if enabled else "border-strong")
            focused = self.hasFocus() and name == self._active
            painter.setPen(QPen(ThemeManager.qcolor("border-focus") if focused else ring, 3 if focused else 2))
            painter.setBrush(ThemeManager.qcolor("gray-0"))
            painter.drawEllipse(QPointF(x, mid), self.HANDLE / 2 - 1.5, self.HANDLE / 2 - 1.5)
        painter.end()
