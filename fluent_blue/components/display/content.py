"""EmptyState, Result, Timeline, ListItem, Tooltip and Popover."""
from __future__ import annotations

from ...compatibility.qt import (
    QEvent,
    QFrame,
    QHBoxLayout,
    QLabel,
    QObject,
    QPainter,
    QPen,
    QPoint,
    QPointF,
    QRectF,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.theme_manager import ThemeManager
from ...icons import icon_pixmap
from ..base import ThemedMixin, check_choice, set_style_prop
from ..buttons.button import Button
from ..popup import PopupShell
from .text import Text


class _Emblem(ThemedMixin, QWidget):
    """Concentric soft rings around an icon: the illustration for empty and result states."""

    def __init__(self, icon: str, tone: str, side: int = 88) -> None:
        super().__init__()
        self._icon, self._tone = icon, tone
        self.setFixedSize(side, side)
        self.bind_theme()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        subtle = {"neutral": "surface-tertiary", "primary": "primary-subtle"}.get(self._tone, f"{self._tone}-subtle")
        accent = {"neutral": "text-tertiary", "primary": "primary-text"}.get(self._tone, f"{self._tone}-text")
        painter.setPen(QPen(ThemeManager.qcolor("border-subtle"), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect.adjusted(.5, .5, -.5, -.5))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor(subtle))
        inset = self.width() * .14
        painter.drawEllipse(rect.adjusted(inset, inset, -inset, -inset))
        px = round(self.width() * .34)
        painter.drawPixmap(QPoint((self.width() - px) // 2, (self.height() - px) // 2), icon_pixmap(self._icon, px, accent))
        painter.end()


class EmptyState(QWidget):
    """Explains why a view is empty and what to do next.

    Args:
        title: Headline.
        description: Supporting text.
        icon: Icon name.
        action_text: Label of the optional action button.

    Signals:
        action_clicked: The action button was used.
    """

    action_clicked = Signal()
    _TONE = "primary"

    def __init__(self, title: str = "Nothing here yet", parent=None, *, description: str = "", icon: str = "inbox",
                 action_text: str = "") -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        layout.addStretch(1)
        self.emblem = _Emblem(icon, self._TONE)
        layout.addWidget(self.emblem, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(8)
        self.title_label = Text(title, style="heading-4", wrap=True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.description_label = Text(description, style="body-medium", color="text-secondary", wrap=True)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setVisible(bool(description))
        layout.addWidget(self.description_label, 0, Qt.AlignmentFlag.AlignHCenter)
        self.actions = QHBoxLayout()
        self.actions.setSpacing(8)
        self.actions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(8)
        layout.addLayout(self.actions)
        layout.addStretch(1)
        self.action_button = None
        if action_text:
            self.action_button = Button(action_text, variant="primary")
            self.action_button.clicked.connect(lambda: self.action_clicked.emit())
            self.actions.addWidget(self.action_button)

    @staticmethod
    def _fit_label(label, width: int) -> None:
        # Wrapped text in a centered column confuses height-for-width, so the labels get an
        # explicit size. The layout's hint is then exact, and nothing can overlap.
        natural = label.fontMetrics().horizontalAdvance(label.text()) + 4
        fitted = min(width, natural)
        label.setFixedWidth(fitted)
        label.setFixedHeight(label.heightForWidth(fitted))

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        width = min(380, max(120, self.width() - 48))
        self._fit_label(self.title_label, width)
        if self.description_label.text():
            self._fit_label(self.description_label, width)
        needed = self.layout().sizeHint().height()
        if needed != self.minimumHeight():
            self.setMinimumHeight(needed)


class Result(EmptyState):
    """The outcome of an operation.

    Args:
        status: ``success``, ``error``, ``warning`` or ``info``.
        title: Headline.
        description: Supporting text.
        action_text: Label of the optional action button.

    Signals:
        action_clicked: The action button was used.
    """

    _ICONS = {"success": "check-circle", "error": "x-circle", "warning": "alert-triangle", "info": "info-circle"}

    def __init__(self, status: str = "success", title: str = "", parent=None, *, description: str = "",
                 action_text: str = "") -> None:
        check_choice("status", status, self._ICONS)
        self._TONE = status
        self.status = status
        super().__init__(title or status.title(), parent, description=description, icon=self._ICONS[status], action_text=action_text)


class _TimelineRow(QWidget):
    def __init__(self, title, description, time, variant, last) -> None:
        super().__init__()
        self._variant, self._last = variant, last
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 0, 0, 16)
        layout.setSpacing(2)
        header = QHBoxLayout()
        header.addWidget(Text(title, style="heading-6"))
        header.addStretch(1)
        if time:
            header.addWidget(Text(time, style="caption", color="text-tertiary"))
        layout.addLayout(header)
        if description:
            layout.addWidget(Text(description, style="body-small", color="text-secondary", wrap=True))

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self._last:
            painter.setPen(QPen(ThemeManager.qcolor("border"), 1))
            painter.drawLine(QPointF(5.5, 16), QPointF(5.5, self.height()))
        role = "primary" if self._variant == "primary" else ("border-strong" if self._variant == "neutral" else self._variant)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor(role))
        painter.drawEllipse(QRectF(1.5, 4, 8, 8))
        painter.end()


class Timeline(QWidget):
    """A vertical sequence of events.

    Args:
        items: Dicts with ``title`` and optional ``description``, ``time`` and ``variant``
            (``primary``, ``neutral``, ``success``, ``warning``, ``error`` or ``info``).
    """

    def __init__(self, items=None, parent=None) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.set_items(items or [])

    def set_items(self, items) -> None:
        """Replace the events."""
        while self._layout.count():
            child = self._layout.takeAt(0).widget()
            if child:
                child.setParent(None)
                child.deleteLater()
        items = list(items)
        for index, item in enumerate(items):
            variant = item.get("variant", "primary")
            check_choice("variant", variant, ("primary", "neutral", "success", "warning", "error", "info"))
            self._layout.addWidget(_TimelineRow(item["title"], item.get("description", ""), item.get("time", ""),
                                                variant, index == len(items) - 1))


class ListItem(ThemedMixin, QFrame):
    """One row of a list.

    Args:
        title: Primary text.
        subtitle: Secondary text.
        icon: Leading icon name.
        leading: Leading widget, such as an ``Avatar``.
        trailing: Trailing widget, such as a ``Badge``.
        clickable: Make the row activatable by mouse and keyboard.
        selected: Initial selected state.

    Signals:
        clicked: A clickable row was activated.
    """

    clicked = Signal()

    def __init__(self, title: str = "", parent=None, *, subtitle: str = "", icon: str | None = None, leading=None,
                 trailing=None, clickable: bool = False, selected: bool = False) -> None:
        super().__init__(parent)
        self._icon, self._clickable = icon, clickable
        self.setProperty("interactive", "true" if clickable else "false")
        self.setProperty("selected", "true" if selected else "false")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        self.icon_label = QLabel()
        self.bind_theme()
        if icon:
            layout.addWidget(self.icon_label)
            self.refresh_theme()
        if leading is not None:
            layout.addWidget(leading)
        column = QVBoxLayout()
        column.setSpacing(0)
        self.title_label = Text(title, style="body-medium")
        column.addWidget(self.title_label)
        if subtitle:
            column.addWidget(Text(subtitle, style="body-small", color="text-tertiary"))
        layout.addLayout(column, 1)
        if trailing is not None:
            layout.addWidget(trailing)
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAccessibleName(f"{title}. {subtitle}" if subtitle else title)

    def set_selected(self, selected: bool) -> None:
        set_style_prop(self, "selected", "true" if selected else "false")

    def is_selected(self) -> bool:
        return self.property("selected") == "true"

    def refresh_theme(self) -> None:
        if self._icon:
            self.icon_label.setPixmap(icon_pixmap(self._icon, 16, "text-secondary"))

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().mouseReleaseEvent(event)
        if self._clickable and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._clickable and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit()
        else:
            super().keyPressEvent(event)


class FloatingTooltip(QFrame):
    """The window drawn by :class:`Tooltip`."""

    def __init__(self, text: str) -> None:
        super().__init__(None, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(text)
        self.label.setMaximumWidth(280)
        self.label.setWordWrap(self.label.sizeHint().width() > 280)
        layout.addWidget(self.label)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor("gray-900"))
        radius = ThemeManager.radius("sm")
        painter.drawRoundedRect(QRectF(self.rect()), radius, radius)
        painter.end()


class Tooltip(QObject):
    """Attach a rich, delayed tooltip to a widget. It also appears on keyboard focus.

    Args:
        target: The widget to describe.
        text: Tooltip text.
        placement: ``top``, ``bottom``, ``left`` or ``right``.
        delay_ms: Hover time before showing.
    """

    def __init__(self, target, text: str, *, placement: str = "top", delay_ms: int = 350) -> None:
        super().__init__(target)
        check_choice("placement", placement, ("top", "bottom", "left", "right"))
        ThemeManager.ensure_applied()
        self.target, self._text, self._placement = target, text, placement
        self.window = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(delay_ms)
        self._timer.timeout.connect(self.show_now)
        target.installEventFilter(self)
        if not target.accessibleDescription():
            target.setAccessibleDescription(text)

    def set_text(self, text: str) -> None:
        self._text = text
        if self.window:
            self.window.label.setText(text)

    def is_visible(self) -> bool:
        return bool(self.window and self.window.isVisible())

    def show_now(self) -> None:
        """Show without waiting for the delay."""
        if self.window is None:
            self.window = FloatingTooltip(self._text)
            self.target.destroyed.connect(self.window.close)
        self.window.adjustSize()
        origin, size, gap = self.target.mapToGlobal(QPoint(0, 0)), self.window.size(), 6
        target = self.target
        x = origin.x() + (target.width() - size.width()) // 2
        y = origin.y() - size.height() - gap
        if self._placement == "bottom":
            y = origin.y() + target.height() + gap
        elif self._placement in ("left", "right"):
            y = origin.y() + (target.height() - size.height()) // 2
            x = origin.x() - size.width() - gap if self._placement == "left" else origin.x() + target.width() + gap
        self.window.move(x, y)
        self.window.show()

    def hide_now(self) -> None:
        self._timer.stop()
        if self.window:
            self.window.hide()

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        kind = event.type()
        if kind in (QEvent.Type.Enter, QEvent.Type.FocusIn):
            self._timer.start()
        elif kind in (QEvent.Type.Leave, QEvent.Type.FocusOut, QEvent.Type.MouseButtonPress, QEvent.Type.Hide):
            self.hide_now()
        return False


class Popover(PopupShell):
    """A floating panel anchored to a widget. It closes on outside click or Escape.

    Args:
        parent: Owner widget.
        title: Optional heading.
        content: Text or a widget.
        width: Panel width in pixels.

    Signals:
        closed: The popover was hidden.
    """

    def __init__(self, parent=None, *, title: str = "", content=None, width: int = 280) -> None:
        super().__init__(parent, padding=12)
        self.setFixedWidth(width + 2 * self.MARGIN)
        self.body.setSpacing(8)
        if title:
            self.body.addWidget(Text(title, style="heading-5"))
        if isinstance(content, str):
            self.body.addWidget(Text(content, style="body-medium", color="text-secondary", wrap=True))
        elif content is not None:
            self.body.addWidget(content)


