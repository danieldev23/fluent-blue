"""Modern Fluent window and custom titlebar system for desktop applications."""
from __future__ import annotations

from ...compatibility.qt import (
    QHBoxLayout,
    QLabel,
    QMouseEvent,
    QPoint,
    QSize,
    Qt,
    QToolButton,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ..base import ThemedMixin, set_style_prop


class TitleBar(ThemedMixin, QWidget):
    """Custom titlebar with native-like window management buttons, draggable area, and branding."""

    def __init__(
        self,
        window: QWidget,
        parent=None,
        *,
        title: str = "",
        icon_name: str | None = None,
        show_minimize: bool = True,
        show_maximize: bool = True,
        show_close: bool = True,
    ) -> None:
        super().__init__(parent or window)
        self.bind_theme()
        self._window = window
        self._drag_pos = QPoint()

        self.setFixedHeight(36)
        set_style_prop(self, "fbComponent", "titleBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(8)

        if icon_name:
            self._icon_lbl = QLabel(self)
            self._icon_lbl.setPixmap(make_icon(icon_name, 16, "primary").pixmap(16, 16))
            layout.addWidget(self._icon_lbl)

        self._title_lbl = QLabel(title, self)
        self._title_lbl.setFont(ThemeManager.font("body-medium"))
        layout.addWidget(self._title_lbl)

        # Draggable flex spacer
        layout.addStretch()

        # Window Controls
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        if show_minimize:
            self._btn_min = QToolButton(self)
            self._btn_min.setIcon(make_icon("minus", 12, "text-secondary"))
            self._btn_min.setFixedSize(44, 36)
            self._btn_min.clicked.connect(self._window.showMinimized)
            set_style_prop(self._btn_min, "winBtn", "min")
            btn_layout.addWidget(self._btn_min)

        if show_maximize:
            self._btn_max = QToolButton(self)
            self._btn_max.setIcon(make_icon("square", 12, "text-secondary"))
            self._btn_max.setFixedSize(44, 36)
            self._btn_max.clicked.connect(self._toggle_maximize)
            set_style_prop(self._btn_max, "winBtn", "max")
            btn_layout.addWidget(self._btn_max)

        if show_close:
            self._btn_close = QToolButton(self)
            self._btn_close.setIcon(make_icon("close", 12, "text-secondary"))
            self._btn_close.setFixedSize(44, 36)
            self._btn_close.clicked.connect(self._window.close)
            set_style_prop(self._btn_close, "winBtn", "close")
            btn_layout.addWidget(self._btn_close)

        layout.addLayout(btn_layout)

    def _toggle_maximize(self) -> None:
        if self._window.isMaximized():
            self._window.showNormal()
        else:
            self._window.showMaximized()

    def set_title(self, title: str) -> None:
        self._title_lbl.setText(title)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt override
        if event.buttons() == Qt.MouseButton.LeftButton and not self._window.isMaximized():
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_maximize()


class FluentWindow(ThemedMixin, QWidget):
    """A frameless base window styled with Fluent Blue design language.

    Features:
    - Custom TitleBar with minimize, maximize, and close controls
    - Central widget host for seamless application layout
    - Native drag and resize support

    Args:
        title: Window title.
        icon_name: Optional icon name from Fluent Blue icon system.
    """

    def __init__(self, parent=None, *, title: str = "Fluent Blue Application", icon_name: str | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.bind_theme()

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Title bar
        self.title_bar = TitleBar(self, title=title, icon_name=icon_name)
        self._main_layout.addWidget(self.title_bar)

        # Content container
        self._content_host = QWidget(self)
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(16, 16, 16, 16)
        self._main_layout.addWidget(self._content_host, stretch=1)

        set_style_prop(self, "fbComponent", "fluentWindow")
        self.resize(1000, 700)

    def set_central_widget(self, widget: QWidget) -> None:
        """Set the main content area widget."""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._content_layout.addWidget(widget)

    def setWindowTitle(self, title: str) -> None:  # noqa: N802 - Qt override
        super().setWindowTitle(title)
        self.title_bar.set_title(title)

