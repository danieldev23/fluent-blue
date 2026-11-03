"""Breadcrumb, tabs and pagination."""
from __future__ import annotations

from ...compatibility.qt import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSize,
    Qt,
    QTabBar,
    QTabWidget,
    QWidget,
    Signal,
)
from ...icons import icon as make_icon
from ...icons import icon_pixmap
from ..base import ThemedMixin


class Breadcrumb(ThemedMixin, QWidget):
    """A trail of links to parent locations; the last entry is the current page.

    Args:
        items: Labels from root to current.

    Signals:
        item_clicked(int, str): Index and label of the activated ancestor.
    """

    item_clicked = Signal(int, str)

    def __init__(self, items=None, parent=None) -> None:
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        self._items: list[str] = []
        self._separators: list[QLabel] = []
        self.bind_theme()
        self.set_items(items or [])

    def items(self) -> list[str]:
        return list(self._items)

    def set_items(self, items) -> None:
        """Replace the trail."""
        self._items = [str(item) for item in items]
        self._rebuild()

    def refresh_theme(self) -> None:
        for separator in self._separators:
            separator.setPixmap(icon_pixmap("chevron-right", 12, "text-tertiary"))

    def _rebuild(self) -> None:
        while self._layout.count():
            child = self._layout.takeAt(0).widget()
            if child:
                child.setParent(None)
                child.deleteLater()
        self._separators = []
        for index, text in enumerate(self._items):
            if index == len(self._items) - 1:
                label = QLabel(text)
                label.setProperty("current", True)
                label.setAccessibleName(f"Current page: {text}")
                self._layout.addWidget(label)
            else:
                button = QPushButton(text)
                button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.clicked.connect(lambda _=False, i=index, t=text: self.item_clicked.emit(i, t))
                self._layout.addWidget(button)
                separator = QLabel()
                separator.setPixmap(icon_pixmap("chevron-right", 12, "text-tertiary"))
                self._separators.append(separator)
                self._layout.addWidget(separator)
        self._layout.addStretch(1)


class TabBar(QTabBar):
    """A standalone tab strip with an underline indicator.

    Args:
        tabs: Initial tab labels.
        closable: Show close buttons.
    """

    def __init__(self, tabs=None, parent=None, *, closable: bool = False) -> None:
        super().__init__(parent)
        self.setExpanding(False)
        self.setDocumentMode(True)
        self.setDrawBase(False)
        self.setTabsClosable(closable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        for text in tabs or []:
            self.addTab(text)


class Tabs(ThemedMixin, QTabWidget):
    """Tabbed pages built on ``QTabWidget``, using :class:`TabBar`.

    Args:
        closable: Show close buttons on tabs.
    """

    def __init__(self, parent=None, *, closable: bool = False) -> None:
        super().__init__(parent)
        self._icons: dict[int, str] = {}
        self.setTabBar(TabBar(closable=closable))
        self.setDocumentMode(True)
        self.setTabsClosable(closable)
        self.bind_theme()

    def add_tab(self, widget, text: str, *, icon: str | None = None) -> int:
        """Add a page and return its index."""
        index = self.addTab(widget, text)
        if icon:
            self._icons[id(widget)] = icon
            self.setTabIcon(index, make_icon(icon, 16, "text-secondary"))
            self.setIconSize(QSize(16, 16))
        return index

    def refresh_theme(self) -> None:
        for index in range(self.count()):
            name = self._icons.get(id(self.widget(index)))
            if name:
                self.setTabIcon(index, make_icon(name, 16, "text-secondary"))


class Pagination(ThemedMixin, QWidget):
    """Page navigation with ellipsis and optional range text.

    Args:
        total: Number of items.
        page_size: Items per page.
        page: Current 1-based page.
        siblings: Pages shown on each side of the current one.
        show_total: Show "1-10 of 200".

    Signals:
        page_changed(int): The new 1-based page.
    """

    page_changed = Signal(int)

    def __init__(self, parent=None, *, total: int = 0, page_size: int = 10, page: int = 1, siblings: int = 1,
                 show_total: bool = True) -> None:
        super().__init__(parent)
        self._total, self._page_size, self._page, self._siblings = max(0, total), max(1, page_size), page, siblings
        self._show_total = show_total
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._group = QButtonGroup(self)
        self.bind_theme()
        self._page = min(max(1, page), self.page_count())
        self._rebuild()

    def page(self) -> int:
        return self._page

    def page_count(self) -> int:
        return max(1, (self._total + self._page_size - 1) // self._page_size)

    def set_page(self, page: int) -> None:
        """Go to a page, clamped to the valid range."""
        page = min(max(1, page), self.page_count())
        if page != self._page:
            self._page = page
            self._rebuild()
            self.page_changed.emit(page)

    def set_total(self, total: int) -> None:
        if max(0, total) == self._total:
            return
        self._total = max(0, total)
        self._page = min(self._page, self.page_count())
        self._rebuild()

    def set_page_size(self, size: int) -> None:
        self._page_size = max(1, size)
        self._page = min(self._page, self.page_count())
        self._rebuild()

    def visible_pages(self) -> list[int | None]:
        """Page numbers to display; ``None`` marks an ellipsis."""
        count, cur, sib = self.page_count(), self._page, self._siblings
        if count <= 5 + 2 * sib:
            return list(range(1, count + 1))
        low, high = max(2, cur - sib), min(count - 1, cur + sib)
        pages: list[int | None] = [1]
        if low > 2:
            pages.append(None)
        pages.extend(range(low, high + 1))
        if high < count - 1:
            pages.append(None)
        pages.append(count)
        return pages

    def refresh_theme(self) -> None:
        for button, icon_name in self._nav_buttons:
            button.setIcon(make_icon(icon_name, 14, "text-secondary"))

    def _nav_button(self, icon_name: str, target: int, enabled: bool, name: str) -> QPushButton:
        button = QPushButton()
        self._nav_buttons.append((button, icon_name))
        button.setIcon(make_icon(icon_name, 14, "text-secondary"))
        button.setEnabled(enabled)
        button.setToolTip(name)
        button.setAccessibleName(name)
        button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda: self.set_page(target))
        return button

    def _rebuild(self) -> None:
        while self._layout.count():
            child = self._layout.takeAt(0).widget()
            if child:
                child.setParent(None)
                child.deleteLater()
        self._nav_buttons = []
        if self._show_total:
            first = (self._page - 1) * self._page_size + 1 if self._total else 0
            last = min(self._page * self._page_size, self._total)
            self._layout.addWidget(QLabel(f"{first:,}–{last:,} of {self._total:,}"))
            self._layout.addSpacing(12)
        self._layout.addStretch(1)
        self._layout.addWidget(self._nav_button("chevron-left", self._page - 1, self._page > 1, "Previous page"))
        for entry in self.visible_pages():
            if entry is None:
                ellipsis = QLabel("…")
                ellipsis.setMinimumWidth(20)
                ellipsis.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._layout.addWidget(ellipsis)
                continue
            button = QPushButton(str(entry))
            button.setCheckable(True)
            button.setChecked(entry == self._page)
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setAccessibleName(f"Page {entry}")
            button.clicked.connect(lambda _=False, p=entry: self._on_click(p))
            self._layout.addWidget(button)
        self._layout.addWidget(self._nav_button("chevron-right", self._page + 1, self._page < self.page_count(), "Next page"))

    def _on_click(self, page: int) -> None:
        if page == self._page:
            self._rebuild()
        else:
            self.set_page(page)
