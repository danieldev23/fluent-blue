"""Alert, Toast, Notification, Snackbar, dialogs and LoadingOverlay."""
from __future__ import annotations

from ...compatibility.qt import (
    QApplication,
    QEvent,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPainter,
    QRectF,
    QSizePolicy,
    Qt,
    QTimer,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.animations import animate, apply_elevation
from ...core.theme_manager import ThemeManager
from ...icons import icon_pixmap
from ..base import ThemedMixin, check_choice, fit_wrapped_labels, paint_spinner
from ..buttons.button import Button, IconButton
from ..display.media import ProgressBar
from ..display.text import Text
from ..layout.overlays import Modal

VARIANTS = ("info", "success", "warning", "error")
_ICONS = {"info": "info-circle", "success": "check-circle", "warning": "alert-triangle", "error": "alert-circle"}


class Alert(ThemedMixin, QFrame):
    """An inline message in the page flow.

    Args:
        title: Bold first line.
        message: Body text.
        variant: ``info``, ``success``, ``warning`` or ``error``.
        closable: Show a dismiss button.
        action_text: Label of an optional action.
        dense: Use tighter spacing and smaller text.

    Signals:
        closed: The alert was dismissed.
        action_clicked: The action was used.
    """

    closed = Signal()
    action_clicked = Signal()

    def __init__(self, title: str = "", message: str = "", parent=None, *, variant: str = "info", closable: bool = False,
                 action_text: str = "", dense: bool = False) -> None:
        super().__init__(parent)
        check_choice("variant", variant, VARIANTS)
        self._variant = variant
        self.setProperty("variant", variant)
        self.setProperty("dense", "true" if dense else "false")
        # Not Maximum: that caps the height at the one-line hint and clips wrapped text.
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setAccessibleName(f"{variant}: {title} {message}".strip())
        row = QHBoxLayout(self)
        row.setContentsMargins(8, 3, 4, 3) if dense else row.setContentsMargins(12, 10, 8, 10)
        row.setSpacing(8 if dense else 10)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(18, 18)
        row.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignVCenter if dense else Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(2)
        if title:
            label = QLabel(title)
            label.setObjectName("alertTitle")
            label.setWordWrap(True)
            column.addWidget(label)
        if message:
            label = QLabel(message)
            label.setObjectName("alertMessage")
            label.setWordWrap(True)
            column.addWidget(label)
        row.addLayout(column, 1)
        if action_text:
            action = Button(action_text, variant="text", size="small")
            action.clicked.connect(lambda: self.action_clicked.emit())
            row.addWidget(action, 0, Qt.AlignmentFlag.AlignTop)
        if closable:
            close = IconButton("close", size="small", tooltip="Dismiss")
            close.clicked.connect(self.dismiss)
            row.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        self.bind_theme()
        self.refresh_theme()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        fit_wrapped_labels(self)

    def dismiss(self) -> None:
        """Hide the alert and emit ``closed``."""
        self.hide()
        self.closed.emit()

    def refresh_theme(self) -> None:
        self.icon_label.setPixmap(icon_pixmap(_ICONS[self._variant], 18, f"{self._variant}-text"))


class ToastCard(ThemedMixin, QFrame):
    """The card behind ``Toast``, ``Notification`` and ``Snackbar``.

    Signals:
        closed: The card finished closing.
        action_clicked: The action was used.
    """

    closed = Signal()
    action_clicked = Signal()

    def __init__(self, *, title: str = "", message: str = "", variant: str | None = None, kind: str = "toast",
                 duration: int = 4000, action_text: str = "", on_action=None, closable: bool = True) -> None:
        super().__init__()
        if variant:
            check_choice("variant", variant, VARIANTS)
        self._variant, self._on_action = variant, on_action
        self.setProperty("kind", kind)
        self.setAccessibleName(f"{title} {message}".strip())
        self.setMaximumWidth(380)
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 8, 10)
        row.setSpacing(10)
        self.icon_label = QLabel()
        # A single line centers with its icon; a title and body align to the first line.
        edge = Qt.AlignmentFlag.AlignTop if title else Qt.AlignmentFlag.AlignVCenter
        if variant:
            self.icon_label.setFixedSize(18, 18)
            row.addWidget(self.icon_label, 0, edge)
        column = QVBoxLayout()
        column.setSpacing(2)
        if title:
            label = QLabel(title)
            label.setObjectName("toastTitle")
            label.setWordWrap(True)
            column.addWidget(label)
        self.message_label = QLabel(message)
        self.message_label.setObjectName("toastMessage")
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumWidth(180)
        column.addWidget(self.message_label)
        row.addLayout(column, 1)
        if action_text:
            action = Button(action_text, variant="text", size="small")
            action.clicked.connect(self._action)
            row.addWidget(action, 0, edge)
        if closable:
            close = IconButton("close", size="small", tooltip="Dismiss")
            close.clicked.connect(self.dismiss)
            row.addWidget(close, 0, edge)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.dismiss)
        self._duration = duration
        if duration > 0:
            self._timer.start(duration)
        self._closing = False
        self.bind_theme()
        self.refresh_theme()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        fit_wrapped_labels(self)

    def refresh_theme(self) -> None:
        apply_elevation(self, 3)
        if self._variant:
            self.icon_label.setPixmap(icon_pixmap(_ICONS[self._variant], 18, f"{self._variant}-text"))

    def dismiss(self) -> None:
        """Animate out, then emit ``closed`` and delete the card."""
        if self._closing:
            return
        self._closing = True
        self._timer.stop()
        animate(self, b"maximumHeight", 0, start=self.height(), duration="fast", on_finished=self._finish)

    def _finish(self) -> None:
        self.hide()
        self.closed.emit()
        self.deleteLater()

    def _action(self) -> None:
        if callable(self._on_action):
            self._on_action()
        self.action_clicked.emit()
        self.dismiss()

    def enterEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().enterEvent(event)
        self._timer.stop()

    def leaveEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().leaveEvent(event)
        if self._duration > 0 and not self._closing:
            self._timer.start(self._duration)


class _OverlayHost(QWidget):
    """A stack of cards anchored to a corner of a window. It sizes to its content."""

    def __init__(self, window, anchor: str) -> None:
        super().__init__(window)
        self._window, self._anchor = window, anchor
        self._cards: list = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        window.installEventFilter(self)

    def add(self, card) -> None:
        self._cards.append(card)
        self.layout().addWidget(card)
        card.closed.connect(lambda: self._forget(card))
        # Show the card now: a widget added to a visible host is shown on the next event
        # loop pass, and a hidden card does not count towards the host's size.
        card.show()
        self.show()
        self._relayout()
        height = self._card_height(card, self.width() - self._horizontal_margins())
        animate(card, b"maximumHeight", height, start=0, duration="fast", on_finished=lambda: self._settle(card))

    def _settle(self, card) -> None:
        card.setMaximumHeight(16777215)
        self._relayout()

    def _forget(self, card) -> None:
        if card in self._cards:
            self._cards.remove(card)
        self._relayout()

    def _live_cards(self) -> list:
        return [c for c in self._cards if c.isVisible()]

    def _horizontal_margins(self) -> int:
        margins = self.layout().contentsMargins()
        return margins.left() + margins.right()

    @staticmethod
    def _card_height(card, width: int) -> int:
        # Wrapped text needs the height for the width the card will get, not the hint.
        layout = card.layout()
        if layout is not None and layout.hasHeightForWidth():
            return layout.totalHeightForWidth(width)
        return card.sizeHint().height()

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if event.type() == QEvent.Type.Resize:
            self._relayout()
        return False

    def _relayout(self) -> None:
        # Size from the cards' hints, not the layout: a card animating its maximum height
        # would otherwise shrink the host and clip its neighbours.
        margins = self.layout().contentsMargins()
        cards = self._live_cards()
        card_width = max([min(c.sizeHint().width(), c.maximumWidth()) for c in cards] + [0])
        width = card_width + margins.left() + margins.right()
        height = sum(self._card_height(c, card_width) for c in cards) + self.layout().spacing() * max(0, len(cards) - 1)
        height += margins.top() + margins.bottom()
        if self._anchor == "top-right":
            self.setGeometry(self._window.width() - width, 0, width, height)
        else:
            self.setGeometry((self._window.width() - width) // 2, self._window.height() - height, width, height)
        self.raise_()


def _host(parent, anchor: str) -> _OverlayHost:
    window = parent.window() if parent is not None else QApplication.activeWindow()
    if window is None:
        raise ValueError("A parent widget or an active window is required to show this message.")
    # Direct children only: a recursive search would walk every widget in the window.
    name = f"_fb_host_{anchor}"
    host = window.findChild(_OverlayHost, name, Qt.FindChildOption.FindDirectChildrenOnly)
    if host is None:
        host = _OverlayHost(window, anchor)
        host.setObjectName(name)
    return host


class Toast:
    """A brief, auto-dismissing message in the window's top right corner."""

    @staticmethod
    def show(message: str, parent=None, *, variant: str = "info", duration: int = 3500) -> ToastCard:
        """Show a toast and return its card.

        Args:
            message: Text.
            parent: Any widget of the target window; defaults to the active window.
            variant: ``info``, ``success``, ``warning`` or ``error``.
            duration: Milliseconds before dismissal, paused on hover. 0 keeps it open.
        """
        card = ToastCard(message=message, variant=variant, duration=duration)
        _host(parent, "top-right").add(card)
        return card


class Notification:
    """A richer message with a title and an action, which stays until dismissed by default."""

    @staticmethod
    def show(title: str, message: str = "", parent=None, *, variant: str = "info", duration: int = 0,
             action_text: str = "", on_action=None) -> ToastCard:
        """Show a notification and return its card.

        Args:
            title: Headline.
            message: Body text.
            parent: Any widget of the target window; defaults to the active window.
            variant: ``info``, ``success``, ``warning`` or ``error``.
            duration: Milliseconds before dismissal; 0 keeps it until dismissed.
            action_text: Action label.
            on_action: Callable to run when the action is used.
        """
        card = ToastCard(title=title, message=message, variant=variant, duration=duration, kind="notification",
                         action_text=action_text, on_action=on_action)
        _host(parent, "top-right").add(card)
        return card


class Snackbar:
    """A single-line message at the bottom center, often offering an undo."""

    @staticmethod
    def show(message: str, parent=None, *, action_text: str = "", on_action=None, duration: int = 4000) -> ToastCard:
        """Show a snackbar and return its card.

        Args:
            message: Text.
            parent: Any widget of the target window; defaults to the active window.
            action_text: Action label, such as ``"Undo"``.
            on_action: Callable to run when the action is used.
            duration: Milliseconds before dismissal.
        """
        card = ToastCard(message=message, kind="snackbar", duration=duration, action_text=action_text,
                         on_action=on_action, closable=False)
        _host(parent, "bottom-center").add(card)
        return card


class MessageDialog(Modal):
    """A modal with a status icon, a message and buttons.

    Args:
        parent: Owner window.
        title: Header title.
        message: Body text.
        variant: ``info``, ``success``, ``warning`` or ``error``.
        buttons: Labels from left to right; the last one is primary.

    Signals:
        button_clicked(str): The label of the chosen button.
    """

    button_clicked = Signal(str)

    def __init__(self, parent=None, *, title: str = "", message: str = "", variant: str = "info", buttons=("OK",), **kwargs) -> None:
        check_choice("variant", variant, VARIANTS)
        super().__init__(parent, title=title, **kwargs)
        self._variant = variant
        self.clicked_button: str | None = None
        row = QHBoxLayout()
        row.setSpacing(12)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        row.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignTop)
        row.addWidget(Text(message, color="text-secondary", wrap=True, selectable=True), 1)
        self.body.addLayout(row)
        self._buttons = {}
        labels = list(buttons)
        for index, label in enumerate(labels):
            button = Button(label, variant=self._button_variant() if index == len(labels) - 1 else "secondary")
            button.clicked.connect(lambda _=False, text=label: self._choose(text))
            self.add_action(button)
            self._buttons[label] = button
        if labels:
            self._buttons[labels[-1]].setDefault(True)
        self.refresh_theme()

    def _button_variant(self) -> str:
        return "primary"

    def button(self, label: str) -> Button:
        return self._buttons[label]

    def refresh_theme(self) -> None:
        super().refresh_theme()
        if hasattr(self, "icon_label"):
            self.icon_label.setPixmap(icon_pixmap(_ICONS[self._variant], 24, f"{self._variant}-text"))

    def _choose(self, label: str) -> None:
        self.clicked_button = label
        self.button_clicked.emit(label)
        self.accept()

    @classmethod
    def show_message(cls, parent, title: str, message: str, variant: str = "info") -> str | None:
        """Block until the dialog closes and return the chosen label."""
        dialog = cls(parent, title=title, message=message, variant=variant)
        dialog.exec()
        return dialog.clicked_button


class ConfirmDialog(MessageDialog):
    """Ask the user to confirm an action.

    Args:
        parent: Owner window.
        title: Header title.
        message: Body text; state the consequence.
        confirm_text: Label of the confirm button; use a verb.
        cancel_text: Label of the cancel button.
        danger: Style the confirm button as destructive.

    Signals:
        confirmed: The action was confirmed.
        cancelled: The dialog closed in any other way.
    """

    confirmed = Signal()
    cancelled = Signal()

    def __init__(self, parent=None, *, title: str = "Are you sure?", message: str = "", confirm_text: str = "Confirm",
                 cancel_text: str = "Cancel", danger: bool = False, **kwargs) -> None:
        self._danger = danger
        self.confirm_text = confirm_text
        kwargs.setdefault("variant", "warning" if danger else "info")
        super().__init__(parent, title=title, message=message, buttons=(cancel_text, confirm_text), **kwargs)
        self.finished.connect(self._emit_outcome)

    def _button_variant(self) -> str:
        return "danger" if self._danger else "primary"

    def was_confirmed(self) -> bool:
        return self.clicked_button == self.confirm_text

    def _emit_outcome(self, _result: int) -> None:
        (self.confirmed if self.was_confirmed() else self.cancelled).emit()

    @classmethod
    def ask(cls, parent, title: str, message: str = "", *, confirm_text: str = "Confirm", danger: bool = False) -> bool:
        """Block until answered. Returns ``True`` if confirmed."""
        dialog = cls(parent, title=title, message=message, confirm_text=confirm_text, danger=danger)
        dialog.exec()
        return dialog.was_confirmed()


class LoadingOverlay(ThemedMixin, QWidget):
    """Blocks a widget and shows a spinner while it is busy.

    Args:
        target: The widget to cover.
        message: Optional text below the spinner.
    """

    def __init__(self, target, *, message: str = "") -> None:
        super().__init__(target)
        self._target, self._message = target, message
        self._angle = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._tick)
        target.installEventFilter(self)
        self.setAccessibleName(message or "Loading")
        self.hide()
        self.bind_theme()

    def start(self, message: str | None = None) -> None:
        """Show the overlay and start spinning."""
        if message is not None:
            self._message = message
        self.setGeometry(self._target.rect())
        self.show()
        self.raise_()
        self._timer.start()

    def stop(self) -> None:
        """Hide the overlay."""
        self._timer.stop()
        self.hide()

    def is_active(self) -> bool:
        return self.isVisible()

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if watched is self._target and event.type() == QEvent.Type.Resize:
            self.setGeometry(self._target.rect())
        return False

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        event.accept()

    def _tick(self) -> None:
        self._angle = (self._angle + 12) % 360
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), ThemeManager.qcolor("surface", .78))
        size = 28
        y = (self.height() - size) / 2 - (12 if self._message else 0)
        paint_spinner(painter, QRectF((self.width() - size) / 2, y, size, size), "primary", self._angle, 3)
        if self._message:
            painter.setFont(ThemeManager.font("body-medium"))
            painter.setPen(ThemeManager.qcolor("text-secondary"))
            area = QRectF(0, y + size + 8, self.width(), 24)
            painter.drawText(area, Qt.AlignmentFlag.AlignCenter, self._message)
        painter.end()


class ProgressDialog(Modal):
    """A modal that reports the progress of a long operation.

    Args:
        parent: Owner window.
        title: Header title.
        message: Status text.
        maximum: Value at completion.
        cancellable: Show a cancel button.
        auto_close: Close automatically at completion.

    Signals:
        canceled: The user asked to cancel.
    """

    canceled = Signal()

    def __init__(self, parent=None, *, title: str = "Working…", message: str = "", maximum: float = 100,
                 cancellable: bool = True, auto_close: bool = True, **kwargs) -> None:
        super().__init__(parent, title=title, closable=False, **kwargs)
        self._auto_close = auto_close
        self._canceled = False
        self.message_label = Text(message, color="text-secondary", wrap=True)
        self.body.addWidget(self.message_label)
        self.bar = ProgressBar(0, maximum=maximum, show_label=True)
        self.body.addWidget(self.bar)
        if cancellable:
            cancel = self.add_action(Button("Cancel"))
            cancel.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            cancel.clicked.connect(self.cancel)

    def value(self) -> float:
        return self.bar.value()

    def set_value(self, value: float) -> None:
        """Update progress; at the maximum the dialog closes if ``auto_close`` is set."""
        self.bar.set_value(value)
        if self._auto_close and self.bar.fraction() >= 1:
            self.accept()

    def set_message(self, message: str) -> None:
        self.message_label.setText(message)

    def was_canceled(self) -> bool:
        return self._canceled

    def cancel(self) -> None:
        """Flag cancellation, emit ``canceled`` and close."""
        self._canceled = True
        self.canceled.emit()
        self.done(0)
