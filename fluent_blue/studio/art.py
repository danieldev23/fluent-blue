"""Original brand artwork, drawn with QPainter from theme tokens and cached per size and theme."""
from __future__ import annotations

from ..compatibility.qt import (
    QColor,
    QFrame,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPointF,
    QPolygonF,
    QRadialGradient,
    QRectF,
    Qt,
    QWidget,
)
from ..components.base import ThemedMixin, device_ratio
from ..core.theme_manager import ThemeManager


def draw_waves(painter: QPainter, rect: QRectF, ribbons: int = 9) -> None:
    """Paint layered translucent ribbons that sweep in from the right edge of ``rect``."""
    q = ThemeManager.qcolor
    w, h, x0, y0 = rect.width(), rect.height(), rect.left(), rect.top()
    for index in range(ribbons):
        t = index / max(1, ribbons - 1)
        path = QPainterPath(QPointF(x0 + w * (.96 - .42 * t), y0 - 2))
        path.cubicTo(QPointF(x0 + w * (.30 + .30 * t), y0 + h * (.12 + .34 * t)),
                     QPointF(x0 + w * (1.08 - .46 * t), y0 + h * (.34 + .22 * t)),
                     QPointF(x0 + w * (.42 + .50 * t), y0 + h + 2))
        path.lineTo(x0 + w + 2, y0 + h + 2)
        path.lineTo(x0 + w + 2, y0 - 2)
        path.closeSubpath()
        gradient = QLinearGradient(x0 + w * .2, y0, x0 + w, y0 + h)
        if index % 2:
            gradient.setColorAt(0, q("primary-100", .30))
            gradient.setColorAt(1, q("primary-500", .34 + .05 * index))
        else:
            gradient.setColorAt(0, q("primary-300", .30 + .04 * index))
            gradient.setColorAt(1, q("primary-700", .26 + .06 * index))
        painter.fillPath(path, gradient)
        painter.strokePath(path, QPen(QColor(255, 255, 255, 54), 1))


class _CachedArt(ThemedMixin, QFrame):
    """Renders ``draw(painter, rect)`` once into a pixmap until the size or theme changes."""

    RADIUS = 12

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cache: QPixmap | None = None
        self.bind_theme()

    def refresh_theme(self) -> None:
        self._cache = None

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._cache = None

    def draw(self, painter: QPainter, rect: QRectF) -> None:
        raise NotImplementedError

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        ratio = device_ratio()
        if self._cache is None:
            self._cache = QPixmap(round(self.width() * ratio), round(self.height() * ratio))
            self._cache.setDevicePixelRatio(ratio)
            self._cache.fill(Qt.GlobalColor.transparent)
            art = QPainter(self._cache)
            art.setRenderHint(QPainter.RenderHint.Antialiasing)
            clip = QPainterPath()
            clip.addRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), self.RADIUS, self.RADIUS)
            art.setClipPath(clip)
            self.draw(art, QRectF(self.rect()))
            art.end()
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._cache)
        painter.end()
        super().paintEvent(event)


class HeroCard(_CachedArt):
    """The Overview banner: a soft blue field with ribbons on the right."""

    def draw(self, painter, rect) -> None:
        q = ThemeManager.qcolor
        field = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if ThemeManager.is_dark():
            field.setColorAt(0, q("surface-secondary"))
            field.setColorAt(1, q("primary-subtle-hover"))
        else:
            field.setColorAt(0, q("primary-50"))
            field.setColorAt(1, q("primary-200"))
        painter.fillRect(rect, field)
        draw_waves(painter, QRectF(rect.width() * .42, 0, rect.width() * .58, rect.height()))


class PromoCard(_CachedArt):
    """The small sidebar card with ribbons along the bottom."""

    def draw(self, painter, rect) -> None:
        q = ThemeManager.qcolor
        field = QLinearGradient(rect.topLeft(), rect.bottomRight())
        field.setColorAt(0, q("primary-400", .55))
        field.setColorAt(1, q("primary-700", .75))
        painter.fillRect(rect, field)
        draw_waves(painter, QRectF(0, rect.height() * .42, rect.width(), rect.height() * .58), 5)


class LandscapeArt(_CachedArt):
    """A generated placeholder picture: sky, sun, ridgelines and a lake."""

    def draw(self, painter, rect) -> None:
        q = ThemeManager.qcolor
        w, h = rect.width(), rect.height()
        sky = QLinearGradient(0, 0, 0, h * .6)
        sky.setColorAt(0, q("primary-400"))
        sky.setColorAt(1, q("primary-100"))
        painter.fillRect(rect, sky)
        sun = QRadialGradient(QPointF(w * .72, h * .26), h * .3)
        sun.setColorAt(0, QColor(255, 255, 255, 230))
        sun.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillRect(rect, sun)
        for depth, (role, base, peak) in enumerate((("primary-300", .50, .22), ("primary-600", .58, .26), ("primary-800", .64, .24))):
            ridge = QPainterPath(QPointF(0, h * base))
            steps = 7
            for step in range(1, steps + 1):
                x = w * step / steps
                y = h * (base - peak * (.5 + .5 * ((step * (depth + 3)) % 5 - 2) / 2) * .8)
                ridge.lineTo(x, y)
            ridge.lineTo(w, h * .66)
            ridge.lineTo(0, h * .66)
            ridge.closeSubpath()
            painter.fillPath(ridge, q(role))
        lake = QLinearGradient(0, h * .66, 0, h)
        lake.setColorAt(0, q("primary-700"))
        lake.setColorAt(1, q("primary-300"))
        painter.fillRect(QRectF(0, h * .66, w, h * .34), lake)


class LogoMark(QWidget):
    """The Fluent Blue mark: an isometric block built from three tinted faces."""

    def __init__(self, size: int = 56, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAccessibleName("Fluent Blue logo")

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = self.width() / 100
        top = QPolygonF([QPointF(50 * s, 6 * s), QPointF(90 * s, 28 * s), QPointF(50 * s, 50 * s), QPointF(10 * s, 28 * s)])
        left = QPolygonF([QPointF(10 * s, 34 * s), QPointF(47 * s, 55 * s), QPointF(47 * s, 96 * s), QPointF(10 * s, 74 * s)])
        right = QPolygonF([QPointF(53 * s, 55 * s), QPointF(90 * s, 34 * s), QPointF(90 * s, 74 * s), QPointF(53 * s, 96 * s)])
        painter.setPen(Qt.PenStyle.NoPen)
        for face, alpha in ((top, 255), (left, 170), (right, 110)):
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawPolygon(face)
        painter.end()
