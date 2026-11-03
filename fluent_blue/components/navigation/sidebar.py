"""Sidebar navigation and top navigation bar."""
from __future__ import annotations

from ...compatibility.qt import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPainter,
    QPushButton,
    QRectF,
    QScrollArea,
    QSize,
    QSizePolicy,
    Qt,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.animations import animate
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ..base import ThemedMixin, apply_common, check_choice


class SidebarItem(ThemedMixin, QPushButton):
    """One navigation entry.

    Args:
        text: Label.
        key: Identifier reported by ``Sidebar.current_changed``; defaults to ``text``.
        icon: Icon name.
        badge: Optional count or short text drawn at the right edge.
        disabled: Start disabled.
        tooltip: Tooltip text; the sidebar uses the label when collapsed.
    """

    def __init__(self, text: str, parent=None, *, key: str | None = None, icon: str | None = None,
                 badge: str | int | None = None, disabled: bool = False, tooltip: str | None = None) -> None:
        super().__init__(text, parent)
        self.key = key or text
        self.label = text
        self.icon_name = icon
        self._badge = None if badge is None else str(badge)
        self._icon_roles = ("text-secondary", "primary-text")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setIconSize(QSize(16, 16))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.bind_theme()
        self.toggled.connect(lambda _on: self.refresh_theme())
        self.refresh_theme()
        apply_common(self, disabled=disabled, tooltip=tooltip)

    def set_icon_roles(self, normal: str, checked: str) -> None:
        """Set the color roles of the icon, for use on non-default sidebar tones."""
        self._icon_roles = (normal, checked)
        self.refresh_theme()

    def set_badge(self, badge: str | int | None) -> None:
        """Set or clear the badge."""
        self._badge = None if badge in (None, "") else str(badge)
        self.update()

    def badge(self) -> str | None:
        return self._badge

    def set_collapsed(self, collapsed: bool) -> None:
        self.setText("" if collapsed else self.label)
        self.setToolTip(self.label if collapsed else "")

    def refresh_theme(self) -> None:
        if self.icon_name:
            role = self._icon_roles[1] if self.isChecked() else self._icon_roles[0]
            self.setIcon(make_icon(self.icon_name, 16, role))

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().paintEvent(event)
        if not self._badge or not self.text():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = ThemeManager.font("caption")
        painter.setFont(font)
        width = max(18, painter.fontMetrics().horizontalAdvance(self._badge) + 10)
        rect = QRectF(self.width() - width - 8, (self.height() - 18) / 2, width, 18)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor("primary"))
        painter.drawRoundedRect(rect, 9, 9)
        painter.setPen(ThemeManager.qcolor("on-primary"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._badge)
        painter.end()


class Sidebar(QFrame):
    """A vertical, sectioned, collapsible navigation rail.

    Args:
        width: Expanded width in pixels.
        collapsed_width: Width in the collapsed state.
        tone: ``default``, or ``brand`` for a blue gradient rail.

    Signals:
        current_changed(str): The key of the newly selected item.
        collapsed_changed(bool): The collapsed state changed.
    """

    current_changed = Signal(str)
    collapsed_changed = Signal(bool)

    def __init__(self, parent=None, *, width: int = 232, collapsed_width: int = 56, tone: str = "default") -> None:
        super().__init__(parent)
        check_choice("tone", tone, ("default", "brand"))
        self._tone = tone
        self.setProperty("tone", tone)
        self._expanded_width = width
        self._collapsed_width = collapsed_width
        self._collapsed = False
        self._items: dict[str, SidebarItem] = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._section_labels: list[QLabel] = []
        self.setFixedWidth(width)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self.header_layout = QVBoxLayout()
        self.header_layout.setContentsMargins(8, 8, 8, 8)
        outer.addLayout(self.header_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        body = QWidget()
        self._body = QVBoxLayout(body)
        self._body.setContentsMargins(8, 0, 8, 8)
        self._body.setSpacing(2)
        self._body.addStretch(1)
        scroll.setWidget(body)
        outer.addWidget(scroll, 1)
        self.footer_layout = QVBoxLayout()
        self.footer_layout.setContentsMargins(8, 8, 8, 8)
        outer.addLayout(self.footer_layout)

    def add_section(self, title: str) -> QLabel:
        """Add a section heading."""
        label = QLabel(title.upper())
        label.setProperty("sidebarSection", True)
        self._section_labels.append(label)
        self._body.insertWidget(self._body.count() - 1, label)
        return label

    def add_item(self, text: str, *, key: str | None = None, icon: str | None = None, badge=None,
                 disabled: bool = False) -> SidebarItem:
        """Add a navigation entry. The first entry added becomes current."""
        item = SidebarItem(text, key=key, icon=icon, badge=badge, disabled=disabled)
        if self._tone == "brand":
            item.set_icon_roles("brand-text-muted", "brand-text")
        if item.key in self._items:
            raise ValueError(f"Duplicate sidebar key: {item.key!r}")
        self._items[item.key] = item
        self._group.addButton(item)
        item.clicked.connect(lambda _=False, k=item.key: self.set_current(k))
        self._body.insertWidget(self._body.count() - 1, item)
        if len(self._items) == 1 and not disabled:
            item.setChecked(True)
        return item

    def item(self, key: str) -> SidebarItem:
        return self._items[key]

    def keys(self) -> list[str]:
        return list(self._items)

    def current(self) -> str | None:
        button = self._group.checkedButton()
        return button.key if button else None

    def set_current(self, key: str) -> None:
        """Select an item and emit ``current_changed``."""
        self._items[key].setChecked(True)
        self.current_changed.emit(key)

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        """Collapse to an icon rail or expand, animated by motion tokens."""
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        for item in self._items.values():
            item.set_collapsed(collapsed)
        for label in self._section_labels:
            label.setVisible(not collapsed)
        target = self._collapsed_width if collapsed else self._expanded_width
        animate(self, b"minimumWidth", target, start=self.width())
        animate(self, b"maximumWidth", target, start=self.width())
        self.collapsed_changed.emit(collapsed)


class NavigationBar(QFrame):
    """A horizontal application bar with title, start, center and end regions.

    Args:
        title: Optional title text.
        height: Bar height in pixels.
    """

    def __init__(self, title: str = "", parent=None, *, height: int = 52) -> None:
        super().__init__(parent)
        self.setFixedHeight(height)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(8)
        self.start_layout = QHBoxLayout()
        self.start_layout.setSpacing(8)
        self.center_layout = QHBoxLayout()
        self.center_layout.setSpacing(8)
        self.end_layout = QHBoxLayout()
        self.end_layout.setSpacing(4)
        self.title_label = QLabel(title)
        self.title_label.setProperty("navTitle", True)
        self.title_label.setVisible(bool(title))
        layout.addLayout(self.start_layout)
        layout.addWidget(self.title_label)
        layout.addStretch(1)
        layout.addLayout(self.center_layout, 2)
        layout.addStretch(1)
        layout.addLayout(self.end_layout)

    def add_start(self, widget) -> None:
        self.start_layout.addWidget(widget)

    def add_center(self, widget) -> None:
        self.center_layout.addWidget(widget)

    def add_end(self, widget) -> None:
        self.end_layout.addWidget(widget)


__all__ = ["NavigationBar", "Sidebar", "SidebarItem"]
