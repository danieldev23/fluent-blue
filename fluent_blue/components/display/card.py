"""Card and StatisticCard."""
from __future__ import annotations

from ...compatibility.qt import QFrame, QHBoxLayout, QLabel, QPainter, QPainterPath, QPen, QPointF, QSizePolicy, Qt, QVBoxLayout, QWidget, Signal
from ...core.animations import apply_elevation
from ...core.theme_manager import ThemeManager
from ...icons import icon_pixmap
from ..base import ThemedMixin, check_choice
from .text import Text


class Card(ThemedMixin, QFrame):
    """A content container.

    With no ``title``, the card has no layout, so you can set your own with
    ``QVBoxLayout(card)``. With a ``title``, it builds a header and exposes :attr:`body`.

    Args:
        title: Header title.
        subtitle: Header subtitle.
        elevation: Shadow level from 0 to 4.
        tone: ``default``, ``secondary`` or ``brand``.
        hoverable: Highlight the border on hover.
        clickable: Make the card activatable by mouse and keyboard.

    Signals:
        clicked: A clickable card was activated.
    """

    clicked = Signal()

    def __init__(self, parent=None, *, title: str = "", subtitle: str = "", elevation: int = 0, tone: str = "default",
                 hoverable: bool = False, clickable: bool = False) -> None:
        super().__init__(parent)
        check_choice("tone", tone, ("default", "secondary", "brand"))
        self._elevation = elevation
        self._clickable = clickable
        self.setProperty("tone", tone)
        self.setProperty("hoverable", "true" if hoverable or clickable else "false")
        self.body = None
        self.bind_theme()
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        if title or subtitle:
            self.body = self.content_layout()
            self.body.setAlignment(Qt.AlignmentFlag.AlignTop)
            if title:
                self.body.addWidget(Text(title, style="heading-4"))
            if subtitle:
                self.body.addWidget(Text(subtitle, style="body-small", color="text-tertiary", wrap=True))
        apply_elevation(self, elevation)

    def content_layout(self) -> QVBoxLayout:
        """Return the card's layout with token padding, creating it if necessary."""
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
            padding = ThemeManager.spacing(4)
            layout.setContentsMargins(padding, padding, padding, padding)
            layout.setSpacing(ThemeManager.spacing(2))
        return layout

    def add(self, widget, stretch: int = 0):
        """Add a widget to the content layout and return it."""
        self.content_layout().addWidget(widget, stretch)
        return widget

    def set_elevation(self, level: int) -> None:
        self._elevation = level
        apply_elevation(self, level)

    def refresh_theme(self) -> None:
        apply_elevation(self, self._elevation)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().mouseReleaseEvent(event)
        if self._clickable and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._clickable and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit()
        else:
            super().keyPressEvent(event)


class _Sparkline(QWidget):
    def __init__(self, values) -> None:
        super().__init__()
        self.values = list(values)
        self.setFixedHeight(36)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        if len(self.values) < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        low, high = min(self.values), max(self.values)
        span = (high - low) or 1
        w, h = self.width() - 2, self.height() - 4
        points = [QPointF(1 + i * w / (len(self.values) - 1), 2 + h - (v - low) / span * h) for i, v in enumerate(self.values)]
        path = QPainterPath(points[0])
        for point in points[1:]:
            path.lineTo(point)
        fill = QPainterPath(path)
        fill.lineTo(points[-1].x(), self.height())
        fill.lineTo(points[0].x(), self.height())
        fill.closeSubpath()
        painter.fillPath(fill, ThemeManager.qcolor("primary", .10))
        pen = QPen(ThemeManager.qcolor("primary"), 1.75)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.strokePath(path, pen)
        painter.end()


class StatisticCard(Card):
    """A headline metric with trend.

    Args:
        title: Metric name.
        value: Formatted value.
        delta: Change text, such as ``"+12.4%"``.
        trend: ``up``, ``down`` or ``flat``. It sets the delta color.
        caption: Text after the delta, such as ``"vs last week"``.
        icon: Icon name.
        spark: Optional numbers for a sparkline.
        positive_is_up: Set ``False`` when a falling number is good, such as error rate.
    """

    def __init__(self, title: str = "", value: str = "", parent=None, *, delta: str = "", trend: str = "flat",
                 caption: str = "", icon: str | None = None, spark=None, positive_is_up: bool = True, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        check_choice("trend", trend, ("up", "down", "flat"))
        self._icon_name = icon
        layout = self.content_layout()
        header = QHBoxLayout()
        header.setSpacing(8)
        self.title_label = Text(title, style="label", color="text-secondary")
        header.addWidget(self.title_label)
        header.addStretch(1)
        self.icon_label = QLabel()
        header.addWidget(self.icon_label)
        layout.addLayout(header)
        self.value_label = Text(value, style="heading-1")
        layout.addWidget(self.value_label)
        if delta or caption:
            row = QHBoxLayout()
            row.setSpacing(6)
            good = (trend == "up") == positive_is_up
            role = "text-secondary" if trend == "flat" else ("success-text" if good else "error-text")
            self.delta_icon = QLabel()
            self._delta_role = role
            self._trend = trend
            if trend != "flat":
                row.addWidget(self.delta_icon)
            self.delta_label = Text(delta, style="label", color=role)
            row.addWidget(self.delta_label)
            row.addWidget(Text(caption, style="body-small", color="text-tertiary"))
            row.addStretch(1)
            layout.addLayout(row)
        else:
            self._trend = None
        if spark:
            self.sparkline = _Sparkline(spark)
            layout.addWidget(self.sparkline)
        self.setAccessibleName(f"{title}: {value}")
        self.refresh_theme()

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def refresh_theme(self) -> None:
        super().refresh_theme()
        if getattr(self, "icon_label", None) is not None and self._icon_name:
            self.icon_label.setPixmap(icon_pixmap(self._icon_name, 16, "text-tertiary"))
        if getattr(self, "_trend", None) in ("up", "down"):
            self.delta_icon.setPixmap(icon_pixmap(f"trending-{self._trend}", 14, self._delta_role))
