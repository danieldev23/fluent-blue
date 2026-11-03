"""Fluent Blue Design Studio main window."""
from __future__ import annotations

import sys

from .. import (
    Avatar, Command, CommandPalette, IconButton, Menu, Popover, Sidebar, ListItem, Text, ThemeManager, Toast, __version__,
)
from ..compatibility.qt import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QPainter, QPoint, QPushButton, QRectF, QSize, QStackedWidget, Qt,
    QVBoxLayout, QWidget,
)
from ..compatibility.qt import delete_now
from ..icons import icon as make_icon
from . import catalog
from .art import LogoMark, PromoCard
from .pages import components, foundations, overview, tools

PRIMARY_NAV = (("Overview", "dashboard"), ("Foundations", "ruler"), ("Colors", "palette"), ("Typography", "type"), ("Icons", "star"))
GROUP_ICONS = {"Buttons": "cursor", "Inputs": "form", "Selection": "toggle", "Navigation": "compass", "Data Display": "chart-pie",
               "Feedback": "bell", "Data Tables": "table", "Layout": "layout", "Advanced Components": "box"}
SIDEBAR_GROUPS = ("Buttons", "Inputs", "Selection", "Navigation", "Data Display", "Feedback", "Data Tables", "Layout", "Advanced Components")
END_NAV = (("Themes", "droplet"), ("Playground", "code"), ("About", "info-circle"), ("Changelog", "refresh"))


class StudioRoot(QWidget):
    """The window background."""

    def __init__(self) -> None:
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)


class _Bell(IconButton):
    """Notification button with a count."""

    def __init__(self, count: int) -> None:
        super().__init__("bell", variant="ghost", tooltip="Notifications")
        self.count = count
        self.setAccessibleName(f"Notifications, {count} unread")

    def set_count(self, count: int) -> None:
        self.count = count
        self.setAccessibleName(f"Notifications, {count} unread")
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().paintEvent(event)
        if not self.count:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        area = QRectF(self.width() - 16, 2, 14, 14)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor("error"))
        painter.drawEllipse(area)
        painter.setPen(ThemeManager.qcolor("on-error"))
        font = ThemeManager.font("caption")
        font.setPixelSize(9)
        painter.setFont(font)
        painter.drawText(area, Qt.AlignmentFlag.AlignCenter, str(self.count))
        painter.end()


class StudioWindow(QMainWindow):
    """The Design Studio. Pages build on first visit."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fluent Blue Design Studio")
        self.setWindowIcon(make_icon("layers", 32, "primary"))
        self.resize(1536, 1024)
        self.setMinimumSize(1024, 680)
        root = StudioRoot()
        self.setCentralWidget(root)
        row = QHBoxLayout(root)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.sidebar = self._build_sidebar()
        row.addWidget(self.sidebar)
        column = QVBoxLayout()
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(self._build_topbar())
        self.stack = QStackedWidget()
        column.addWidget(self.stack, 1)
        row.addLayout(column, 1)
        self.pages: dict[str, QWidget] = {}
        self.palette_widget = CommandPalette(self, commands=self._commands(), placeholder="Search components…")
        self.sidebar.current_changed.connect(self.show_page)
        ThemeManager.theme_about_to_change.connect(self._on_theme_about_to_change)
        self.show_page("Overview")

    # ---- chrome --------------------------------------------------------------------------
    def _build_sidebar(self) -> Sidebar:
        side = Sidebar(width=196, tone="brand")
        brand = QVBoxLayout()
        brand.setContentsMargins(10, 16, 6, 12)
        brand.setSpacing(2)
        brand.addWidget(LogoMark(52))
        brand.addSpacing(10)
        brand.addWidget(Text("PyQt", style="heading-3", color="brand-text"))
        brand.addWidget(Text("Design System", style="body-large", color="brand-text"))
        brand.addSpacing(6)
        brand.addWidget(Text("Fluent Blue", style="heading-2", color="brand-text"))
        brand.addWidget(Text("Modern. Clean. Productive.", style="body-small", color="brand-text-muted"))
        brand.addSpacing(10)
        version = QLabel(f"v{__version__}")
        version.setObjectName("versionPill")
        brand.addWidget(version, 0, Qt.AlignmentFlag.AlignLeft)
        side.header_layout.addLayout(brand)
        for name, icon in PRIMARY_NAV:
            side.add_item(name, icon=icon)
        side.add_section("Components")
        for group in SIDEBAR_GROUPS:
            side.add_item(group, icon=GROUP_ICONS[group])
        side.add_section("Studio")
        for name, icon in END_NAV:
            side.add_item(name, icon=icon)
        promo = self.promo = PromoCard()
        promo.setFixedHeight(120)
        inner = QVBoxLayout(promo)
        inner.setContentsMargins(14, 12, 14, 12)
        inner.addWidget(Text("Built for PyQt6 & PySide6", style="heading-6", color="brand-text", wrap=True))
        inner.addWidget(Text("Beautiful UI,\nmore productive.", style="caption", color="brand-text"))
        inner.addStretch(1)
        side.footer_layout.addWidget(promo)
        return side

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(64)
        row = QHBoxLayout(bar)
        row.setContentsMargins(24, 12, 20, 8)
        row.setSpacing(6)
        self.search_pill = QPushButton("Search components…   (Ctrl+K)")
        self.search_pill.setObjectName("searchPill")
        self.search_pill.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_pill.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.search_pill.setIconSize(QSize(16, 16))
        self.search_pill.clicked.connect(lambda: self.palette_widget.open_palette())
        self.search_pill.setMaximumWidth(680)
        row.addWidget(self.search_pill, 3)
        row.addStretch(1)
        self.sun = IconButton("sun", tooltip="Light theme", checkable=True)
        self.moon = IconButton("moon", tooltip="Dark theme", checkable=True)
        self.sun.clicked.connect(lambda: self._set_theme("light"))
        self.moon.clicked.connect(lambda: self._set_theme("dark"))
        row.addWidget(self.sun)
        row.addWidget(self.moon)
        divider = QFrame()
        divider.setFixedSize(1, 24)
        divider.setProperty("topbarDivider", True)
        row.addSpacing(6)
        row.addWidget(divider)
        row.addSpacing(6)
        self.bell = _Bell(3)
        self.notifications = self._notification_popover()
        self.bell.clicked.connect(lambda: self.notifications.show_at(self.bell))
        row.addWidget(self.bell)
        self.user = _AvatarButton("Alex Morgan")
        self.user.clicked.connect(self._show_user_menu)
        row.addWidget(self.user)
        ThemeManager.theme_changed.connect(self._sync_topbar)
        self._sync_topbar()
        return bar

    def _notification_popover(self) -> Popover:
        pop = Popover(self, title="Notifications", width=320)
        rows = (("Build passed", "All tests are green", "check-circle"), ("New icon set", "131 icons are available", "star"), ("Theme updated", "Dark surfaces were refined", "palette"))
        for title, note, icon in rows:
            pop.body.addWidget(ListItem(title, subtitle=note, icon=icon))
        pop.closed.connect(lambda: self.bell.set_count(0))
        return pop

    def _show_user_menu(self) -> None:
        menu = Menu(self, items=[
            {"text": "Profile", "icon": "user"}, {"text": "Preferences", "icon": "settings"}, None,
            {"text": "About", "icon": "info-circle", "id": "About"},
        ])
        menu.item_triggered.connect(self._on_user_item)
        menu.popup(self.user.mapToGlobal(QPoint(0, self.user.height() + 4)))

    def _on_user_item(self, item: str) -> None:
        if item == "About":
            self.navigate("About")
        else:
            Toast.show(f"{item} is a demo menu entry", parent=self, duration=1600)

    def _set_theme(self, name: str) -> None:
        ThemeManager.set_theme(name)
        self._sync_topbar()

    def _sync_topbar(self, _name: str = "") -> None:
        self.sun.setChecked(not ThemeManager.is_dark())
        self.moon.setChecked(ThemeManager.is_dark())
        self.search_pill.setIcon(make_icon("search", 16, "text-secondary"))

    def _commands(self) -> list[Command]:
        commands = []
        for entry in catalog.entries():
            commands.append(Command(f"component:{entry.group}:{entry.name}", entry.name, entry.group, "box",
                                    action=lambda e=entry: self.reveal(e.group, e.name)))
        for name, icon in (*PRIMARY_NAV, *END_NAV):
            commands.append(Command(f"page:{name}", name, "Page", icon, action=lambda n=name: self.navigate(n)))
        commands.append(Command("theme:toggle", "Toggle light and dark", "Theme", "moon", action=ThemeManager.toggle))
        return commands

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self.promo.setVisible(self.height() >= 860)  # Give navigation the room on short screens.

    # ---- navigation ------------------------------------------------------------------------
    def navigate(self, name: str) -> None:
        """Select a page, updating the sidebar."""
        self.sidebar.set_current(name)

    def reveal(self, group: str, name: str) -> None:
        """Open a component group and scroll to one component."""
        self.navigate(group)
        page = self.pages[group]
        QApplication.processEvents()
        page.reveal(name)

    def show_page(self, name: str) -> None:
        """Show a page, building it on first visit."""
        page = self.pages.get(name)
        if page is None:
            page = self._build_page(name)
            self.pages[name] = page
            self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)
        self._drop_hidden_pages(keep=3)

    def _on_theme_about_to_change(self, _name: str) -> None:
        self._drop_hidden_pages()

    def _drop_hidden_pages(self, keep: int = 0) -> None:
        """Destroy hidden pages, which rebuild quickly on the next visit.

        Stylesheet changes visit every live widget, so this is what keeps a theme switch fast.
        """
        current = self.stack.currentWidget()
        # Overview is the costliest to rebuild, and Playground holds the user's code.
        hidden = [n for n, p in self.pages.items() if p is not current and n not in ("Overview", "Playground")]
        for name in hidden[:max(0, len(hidden) - keep)]:
            page = self.pages.pop(name)
            self.stack.removeWidget(page)
            page.setParent(None)
            delete_now(page)

    def _build_page(self, name: str) -> QWidget:
        if name == "Overview":
            page = overview.OverviewPage()
            page.navigate.connect(self.navigate)
            return page
        builders = {
            "Foundations": foundations.foundations_page, "Colors": foundations.colors_page, "Typography": foundations.typography_page,
            "Icons": foundations.IconsPage, "Themes": tools.themes_page, "Playground": tools.PlaygroundPage, "About": tools.about_page,
            "Changelog": tools.changelog_page,
        }
        if name in builders:
            return builders[name]()
        return components.ComponentGroupPage(name)


class _AvatarButton(QPushButton):
    """An avatar that behaves as a button."""

    def __init__(self, name: str) -> None:
        super().__init__()
        self.setFixedSize(40, 40)
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAccessibleName(f"Account: {name}")
        self.setStyleSheet("")
        avatar = Avatar(name, self, size=36)
        avatar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        avatar.move(2, 2)


def main() -> int:
    """Run Design Studio."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Fluent Blue Design Studio")
    ThemeManager.set_theme("light")
    window = StudioWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

