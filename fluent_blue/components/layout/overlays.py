"""Modal and Drawer."""
from __future__ import annotations

from ...compatibility.qt import QDialog, QEvent, QFrame, QHBoxLayout, QPoint, QRect, Qt, QVBoxLayout, QWidget, Signal
from ...core.animations import animate, apply_elevation
from ..base import ThemedMixin, check_choice
from ..buttons.button import IconButton
from ..display.text import Text


class ModalScrim(QWidget):
    """Dims a window behind an overlay and tracks its size."""

    clicked = Signal()

    def __init__(self, window) -> None:
        super().__init__(window)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setGeometry(window.rect())
        window.installEventFilter(self)

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if event.type() == QEvent.Type.Resize:
            self.setGeometry(watched.rect())
        return False

    def mousePressEvent(self, _event) -> None:  # noqa: N802 - Qt override
        self.clicked.emit()


class DrawerScrim(ModalScrim):
    """The scrim of a :class:`Drawer`."""


class Modal(ThemedMixin, QDialog):
    """A themed modal dialog over a dimmed parent window.

    Args:
        parent: Owner window.
        title: Header title.
        content: Text or a widget for the body.
        width: Panel width in pixels.
        closable: Allow closing with the header button and Escape.

    Attributes:
        body: Layout of the content area.
        footer: Layout of the action row. It is hidden while empty.

    Signals:
        closed: The dialog was hidden, regardless of outcome.
        Inherits ``accepted`` and ``rejected`` from ``QDialog``.
    """

    closed = Signal()
    MARGIN = 0

    def __init__(self, parent=None, *, title: str = "", content=None, width: int = 460, closable: bool = True) -> None:
        super().__init__(parent)
        self._closable = closable
        self._scrim = None
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("QDialog { background: transparent; }")
        self.setModal(True)
        self.setAccessibleName(title or "Dialog")
        self.setFixedWidth(width)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.panel = QFrame()
        self.panel.setObjectName("modalPanel")
        outer.addWidget(self.panel)
        column = QVBoxLayout(self.panel)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        header = QHBoxLayout()
        header.setContentsMargins(20, 16, 12, 8)
        self.title_label = Text(title)
        self.title_label.setObjectName("modalTitle")
        header.addWidget(self.title_label, 1)
        self.close_button = IconButton("close", size="small", tooltip="Close")
        self.close_button.clicked.connect(self.reject)
        self.close_button.setVisible(closable)
        header.addWidget(self.close_button, 0, Qt.AlignmentFlag.AlignTop)
        column.addLayout(header)
        holder = QWidget()
        self.body = QVBoxLayout(holder)
        self.body.setContentsMargins(20, 4, 20, 16)
        self.body.setSpacing(8)
        column.addWidget(holder, 1)
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("modalFooter")
        self.footer = QHBoxLayout(self.footer_frame)
        self.footer.setContentsMargins(20, 12, 20, 12)
        self.footer.setSpacing(8)
        self.footer.addStretch(1)
        self.footer_frame.setVisible(False)
        column.addWidget(self.footer_frame)
        if isinstance(content, str):
            self.body.addWidget(Text(content, color="text-secondary", wrap=True, selectable=True))
        elif content is not None:
            self.body.addWidget(content)
        self.bind_theme()
        apply_elevation(self.panel, 4)

    def add_action(self, button):
        """Add a button to the footer and return it."""
        self.footer.addWidget(button)
        self.footer_frame.setVisible(True)
        return button

    def refresh_theme(self) -> None:
        apply_elevation(self.panel, 4)

    def reject(self) -> None:
        if self._closable:
            super().reject()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().showEvent(event)
        owner = self.parentWidget().window() if self.parentWidget() else None
        if owner is not None:
            if self._scrim is None:
                self._scrim = ModalScrim(owner)
            self._scrim.setGeometry(owner.rect())
            self._scrim.show()
            self._scrim.raise_()
            self.adjustSize()
            corner = owner.mapToGlobal(QPoint(0, 0))
            self.move(corner.x() + (owner.width() - self.width()) // 2,
                      corner.y() + max(0, (owner.height() - self.height()) // 2))

    def hideEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().hideEvent(event)
        if self._scrim is not None:
            self._scrim.hide()
        self.closed.emit()


class Drawer(ThemedMixin, QFrame):
    """A panel that slides in from the edge of a window.

    Args:
        parent: Any widget in the target window.
        title: Header title.
        placement: ``left`` or ``right``.
        width: Panel width in pixels.
        dismissible: Close on Escape and on clicks on the scrim.

    Signals:
        opened: The drawer started opening.
        closed: The drawer finished closing.
    """

    opened = Signal()
    closed = Signal()

    def __init__(self, parent, *, title: str = "", placement: str = "right", width: int = 360, dismissible: bool = True) -> None:
        check_choice("placement", placement, ("left", "right"))
        host = parent.window()
        super().__init__(host)
        self._placement, self._width, self._dismissible = placement, width, dismissible
        self._host = host
        self._open = False
        self._scrim = DrawerScrim(host)
        self._scrim.hide()
        if dismissible:
            self._scrim.clicked.connect(self.close_drawer)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        header = QHBoxLayout()
        header.setContentsMargins(20, 16, 12, 8)
        self.title_label = Text(title)
        self.title_label.setObjectName("modalTitle")
        header.addWidget(self.title_label, 1)
        close = IconButton("close", size="small", tooltip="Close")
        close.clicked.connect(self.close_drawer)
        header.addWidget(close)
        layout.addLayout(header)
        holder = QWidget()
        self.body = QVBoxLayout(holder)
        self.body.setContentsMargins(20, 8, 20, 20)
        self.body.setSpacing(8)
        layout.addWidget(holder, 1)
        self.hide()
        self.setAccessibleName(title or "Drawer")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.bind_theme()
        apply_elevation(self, 4)
        host.installEventFilter(self)

    def add(self, widget, stretch: int = 0):
        """Add a widget to the body and return it."""
        self.body.addWidget(widget, stretch)
        return widget

    def is_open(self) -> bool:
        return self._open

    def _rect(self, shown: bool) -> QRect:
        host = self._host.rect()
        if self._placement == "right":
            x = host.width() - self._width if shown else host.width()
        else:
            x = 0 if shown else -self._width
        return QRect(x, 0, self._width, host.height())

    def open_drawer(self) -> None:
        """Slide the drawer in and move focus to it."""
        if self._open:
            return
        self._open = True
        self._scrim.setGeometry(self._host.rect())
        self._scrim.show()
        self._scrim.raise_()
        self.setGeometry(self._rect(False))
        self.show()
        self.raise_()
        self.setFocus()
        animate(self, b"geometry", self._rect(True), start=self._rect(False), duration="slow", easing="emphasized")
        self.opened.emit()

    def close_drawer(self) -> None:
        """Slide the drawer out."""
        if not self._open:
            return
        self._open = False
        animate(self, b"geometry", self._rect(False), start=self.geometry(), duration="normal", on_finished=self._finish_close)

    def _finish_close(self) -> None:
        self.hide()
        self._scrim.hide()
        self.closed.emit()

    def refresh_theme(self) -> None:
        apply_elevation(self, 4)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() == Qt.Key.Key_Escape and self._dismissible:
            self.close_drawer()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if watched is self._host and event.type() == QEvent.Type.Resize and self._open:
            self.setGeometry(self._rect(True))
        return False
