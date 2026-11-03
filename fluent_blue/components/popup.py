"""Shared popup window: a rounded panel with a themed shadow, placed next to an anchor."""
from __future__ import annotations

from ..compatibility.qt import QFrame, QGuiApplication, QPoint, Qt, QVBoxLayout, Signal
from ..core.animations import apply_elevation
from .base import ThemedMixin


class PopupShell(ThemedMixin, QFrame):
    """Base for popups. Add content to :attr:`body`; the outer margin holds the shadow.

    Signals:
        closed: The popup was hidden.
    """

    closed = Signal()
    MARGIN = 14

    def __init__(self, parent=None, *, elevation: int = 3, padding: int = 4) -> None:
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._elevation = elevation
        outer = QVBoxLayout(self)
        outer.setContentsMargins(self.MARGIN, self.MARGIN, self.MARGIN, self.MARGIN)
        self.panel = QFrame()
        self.panel.setProperty("popupPanel", True)
        outer.addWidget(self.panel)
        self.body = QVBoxLayout(self.panel)
        self.body.setContentsMargins(padding, padding, padding, padding)
        self.body.setSpacing(4)
        self.bind_theme()
        apply_elevation(self.panel, elevation)

    def refresh_theme(self) -> None:
        apply_elevation(self.panel, self._elevation)

    def show_at(self, anchor, placement: str = "bottom", gap: int = 4) -> None:
        """Show next to ``anchor`` (``top``, ``bottom``, ``left``, ``right``), kept on screen."""
        self.ensurePolished()
        size = self.size() if self.testAttribute(Qt.WidgetAttribute.WA_Resized) else self.sizeHint()
        self.resize(size)
        m = self.MARGIN
        origin = anchor.mapToGlobal(QPoint(0, 0))
        x, y = origin.x() - m, origin.y() + anchor.height() + gap - m
        if placement == "top":
            y = origin.y() - size.height() - gap + m
        elif placement == "right":
            x, y = origin.x() + anchor.width() + gap - m, origin.y() - m
        elif placement == "left":
            x, y = origin.x() - size.width() - gap + m, origin.y() - m
        screen = QGuiApplication.screenAt(origin) or QGuiApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            x = max(area.left(), min(x, area.right() - size.width()))
            y = max(area.top(), min(y, area.bottom() - size.height()))
        self.move(x, y)
        self.show()

    def hideEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().hideEvent(event)
        self.closed.emit()
