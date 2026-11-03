"""Avatar, AvatarGroup, progress indicators and Skeleton."""
from __future__ import annotations

import zlib

from ...compatibility.qt import (
    QBrush,
    QHBoxLayout,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRectF,
    QSize,
    QSizePolicy,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.palette import readable_on
from ...core.theme_manager import ThemeManager
from ..base import ThemedMixin, check_choice

_AVATAR_ROLES = ("primary", "success", "warning", "error", "info", "primary-700", "gray-600")
_SIZES = {"small": 24, "medium": 32, "large": 44, "xl": 64}


class Avatar(ThemedMixin, QWidget):
    """A user image or initials.

    Args:
        name: Used for initials, the fallback color and the accessible name.
        image: Image path or ``QPixmap``.
        size: ``small``, ``medium``, ``large``, ``xl`` or a pixel size.
        shape: ``circle`` or ``square``.
        status: Optional presence dot: ``online``, ``away``, ``busy`` or ``offline``.
    """

    _STATUS = {"online": "success", "away": "warning", "busy": "error", "offline": "gray-400"}

    def __init__(self, name: str = "", parent=None, *, image=None, size="medium", shape: str = "circle",
                 status: str | None = None) -> None:
        super().__init__(parent)
        check_choice("shape", shape, ("circle", "square"))
        if status is not None:
            check_choice("status", status, self._STATUS)
        self._name, self._shape, self._status = name, shape, status
        self._side = size if isinstance(size, int) else _SIZES[size]
        self._pixmap = QPixmap(image) if isinstance(image, str) else image
        self.setFixedSize(self._side, self._side)
        self.setAccessibleName(name)
        self.bind_theme()

    def initials(self) -> str:
        parts = self._name.split()
        if not parts:
            return "?"
        return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()

    def set_image(self, image) -> None:
        self._pixmap = QPixmap(image) if isinstance(image, str) else image
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(self._side, self._side)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(self.rect())
        path = QPainterPath()
        radius = self._side / 2 if self._shape == "circle" else ThemeManager.radius("md")
        path.addRoundedRect(rect, radius, radius)
        painter.save()
        painter.setClipPath(path)
        if self._pixmap and not self._pixmap.isNull():
            painter.drawPixmap(self.rect(), self._pixmap)
        else:
            role = _AVATAR_ROLES[zlib.crc32(self._name.encode()) % len(_AVATAR_ROLES)]
            painter.fillRect(rect, ThemeManager.qcolor(role))
            font = ThemeManager.font("label")
            font.setPixelSize(max(9, round(self._side * .38)))
            painter.setFont(font)
            ink = readable_on(ThemeManager.color(role)[:7], ThemeManager.color("gray-0"), ThemeManager.color("gray-950"))
            painter.setPen(ThemeManager.qcolor(ink))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.initials())
        painter.restore()
        if self._status:
            dot = max(7, self._side * .28)
            area = QRectF(self._side - dot, self._side - dot, dot, dot)
            painter.setPen(QPen(ThemeManager.qcolor("surface"), 1.5))
            painter.setBrush(ThemeManager.qcolor(self._STATUS[self._status]))
            painter.drawEllipse(area)
        painter.end()


class AvatarGroup(QWidget):
    """Overlapping avatars with a "+N" overflow.

    Args:
        names: People to display.
        max_visible: Avatars shown before the overflow counter.
        size: Avatar size name.
    """

    def __init__(self, names=None, parent=None, *, max_visible: int = 4, size: str = "medium") -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        names = list(names or [])
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        side = _SIZES[size]
        layout.setSpacing(-round(side * .28))
        for name in names[:max_visible]:
            layout.addWidget(Avatar(name, size=size))
        self.overflow = len(names) - max_visible if len(names) > max_visible else 0
        if self.overflow:
            more = _Overflow(f"+{self.overflow}", side)
            layout.addWidget(more)
        self.setAccessibleName(", ".join(names))


class _Overflow(QWidget):
    def __init__(self, text: str, side: int) -> None:
        super().__init__()
        self._text = text
        self.setFixedSize(side, side)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(ThemeManager.qcolor("surface"), 1))
        painter.setBrush(ThemeManager.qcolor("surface-tertiary"))
        painter.drawEllipse(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5))
        painter.setFont(ThemeManager.font("caption"))
        painter.setPen(ThemeManager.qcolor("text-secondary"))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)
        painter.end()


class _Progress(QWidget):
    """Shared value handling and the indeterminate clock."""

    value_changed = Signal(float)

    def __init__(self, value, parent, minimum, maximum, indeterminate, variant) -> None:
        super().__init__(parent)
        check_choice("variant", variant, ("primary", "success", "warning", "error", "info"))
        ThemeManager.ensure_applied()
        self._minimum, self._maximum, self._value = minimum, maximum, value
        self._variant, self._indeterminate = variant, indeterminate
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._advance)
        self.setAccessibleName("Progress")

    def value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        """Set the value, clamped to the bounds."""
        value = min(max(value, self._minimum), self._maximum)
        if value != self._value:
            self._value = value
            self.update()
            self.value_changed.emit(value)

    def fraction(self) -> float:
        span = self._maximum - self._minimum
        return (self._value - self._minimum) / span if span else 0.0

    def is_indeterminate(self) -> bool:
        return self._indeterminate

    def set_indeterminate(self, on: bool) -> None:
        self._indeterminate = on
        self._sync_timer()
        self.update()

    def _sync_timer(self) -> None:
        if self._indeterminate and self.isVisible():
            self._timer.start()
        else:
            self._timer.stop()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().showEvent(event)
        self._sync_timer()

    def hideEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().hideEvent(event)
        self._timer.stop()

    def _advance(self) -> None:
        self._phase = (self._phase + .018) % 1.0
        self.update()


class ProgressBar(_Progress):
    """A horizontal progress bar.

    Args:
        value: Current value.
        minimum: Lower bound.
        maximum: Upper bound.
        indeterminate: Animate without a known value.
        variant: ``primary``, ``success``, ``warning``, ``error`` or ``info``.
        show_label: Show the percentage at the right.
        thickness: Track height in pixels.

    Signals:
        value_changed(float): The value changed.
    """

    def __init__(self, value: float = 0, parent=None, *, minimum: float = 0, maximum: float = 100,
                 indeterminate: bool = False, variant: str = "primary", show_label: bool = False, thickness: int = 6) -> None:
        super().__init__(value, parent, minimum, maximum, indeterminate, variant)
        self._show_label, self._thickness = show_label, thickness
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(160, max(self._thickness, 18 if self._show_label else 0))

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        width = self.width() - (44 if self._show_label else 0)
        top = (self.height() - self._thickness) / 2
        radius = self._thickness / 2
        track = QRectF(0, top, width, self._thickness)
        painter.setBrush(ThemeManager.qcolor("surface-tertiary"))
        painter.drawRoundedRect(track, radius, radius)
        painter.setBrush(ThemeManager.qcolor(self._variant))
        if self._indeterminate:
            span = width * .32
            x = self._phase * (width + span) - span
            clip = QPainterPath()
            clip.addRoundedRect(track, radius, radius)
            painter.setClipPath(clip)
            painter.drawRoundedRect(QRectF(x, top, span, self._thickness), radius, radius)
            painter.setClipping(False)
        elif self.fraction() > 0:
            painter.drawRoundedRect(QRectF(0, top, max(self._thickness, width * self.fraction()), self._thickness), radius, radius)
        if self._show_label:
            painter.setPen(ThemeManager.qcolor("text-secondary"))
            painter.setFont(ThemeManager.font("body-small"))
            label = "…" if self._indeterminate else f"{round(self.fraction() * 100)}%"
            area = QRectF(width, 0, 44, self.height())
            painter.drawText(area, int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter), label)
        painter.end()


class CircularProgress(_Progress):
    """A circular progress indicator, which also serves as a spinner.

    Args:
        value: Current value.
        minimum: Lower bound.
        maximum: Upper bound.
        indeterminate: Spin without a known value.
        variant: ``primary``, ``success``, ``warning``, ``error`` or ``info``.
        size: Outer diameter in pixels.
        thickness: Stroke width in pixels.
        show_label: Show the percentage at the center.

    Signals:
        value_changed(float): The value changed.
    """

    def __init__(self, value: float = 0, parent=None, *, minimum: float = 0, maximum: float = 100,
                 indeterminate: bool = False, variant: str = "primary", size: int = 48, thickness: int = 4,
                 show_label: bool = True) -> None:
        super().__init__(value, parent, minimum, maximum, indeterminate, variant)
        self._thickness, self._show_label = thickness, show_label
        self.setFixedSize(size, size)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        inset = self._thickness / 2 + .5
        area = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        painter.setPen(QPen(ThemeManager.qcolor("surface-tertiary"), self._thickness))
        painter.drawEllipse(area)
        pen = QPen(ThemeManager.qcolor(self._variant), self._thickness)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        if self._indeterminate:
            painter.drawArc(area, int(-self._phase * 360 * 16), 100 * 16)
        else:
            painter.drawArc(area, 90 * 16, int(-self.fraction() * 360 * 16))
            if self._show_label and self.width() >= 36:
                painter.setPen(ThemeManager.qcolor("text-primary"))
                painter.setFont(ThemeManager.font("caption"))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{round(self.fraction() * 100)}%")
        painter.end()


class _SkeletonBlock(QWidget):
    def __init__(self, owner, height: int, radius: float, width: int | None = None) -> None:
        super().__init__()
        self.owner, self._radius = owner, radius
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        base, shine = ThemeManager.qcolor("surface-tertiary"), ThemeManager.qcolor("border-subtle")
        w = max(1, self.width())
        x = self.owner.phase * (w * 2) - w / 2
        gradient = QLinearGradient(x - w / 2, 0, x + w / 2, 0)
        gradient.setColorAt(0, base)
        gradient.setColorAt(.5, shine)
        gradient.setColorAt(1, base)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(QRectF(self.rect()), self._radius, self._radius)
        painter.end()


class Skeleton(QWidget):
    """A placeholder with a soft shimmer while content loads. The timer stops while hidden.

    Args:
        shape: ``text``, ``rect`` or ``circle``.
        lines: Number of lines for the ``text`` shape.
        width: Width for ``rect`` and ``circle``.
        height: Height for ``rect``.
    """

    def __init__(self, parent=None, *, shape: str = "text", lines: int = 3, width: int | None = None, height: int = 80) -> None:
        super().__init__(parent)
        check_choice("shape", shape, ("text", "rect", "circle"))
        ThemeManager.ensure_applied()
        self.phase = 0.0
        self.setAccessibleName("Loading")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self._blocks = []
        if shape == "text":
            for index in range(lines):
                block = _SkeletonBlock(self, 12, 4)
                self._blocks.append(block)
                layout.addWidget(block)
                if index == lines - 1 and lines > 1:
                    layout.setAlignment(block, Qt.AlignmentFlag.AlignLeft)
                    block.setFixedWidth(180)
        elif shape == "circle":
            side = width or 40
            self._blocks.append(_SkeletonBlock(self, side, side / 2, side))
            layout.addWidget(self._blocks[0])
        else:
            self._blocks.append(_SkeletonBlock(self, height, ThemeManager.radius("md"), width))
            layout.addWidget(self._blocks[0])
        self.setSizePolicy(QSizePolicy.Policy.Preferred if shape != "text" else QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._advance)

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().showEvent(event)
        self._timer.start()

    def hideEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().hideEvent(event)
        self._timer.stop()

    def _advance(self) -> None:
        self.phase = (self.phase + .02) % 1.0
        for block in self._blocks:
            block.update()
