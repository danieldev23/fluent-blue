"""Menu, MenuItem and DropdownMenu."""
from __future__ import annotations

from ...compatibility.qt import QAction, QMenu, Qt, Signal
from ...icons import icon as make_icon
from ..base import ThemedMixin
from ..buttons.button import Button


class MenuItem(QAction):
    """A menu entry.

    Args:
        text: Label.
        parent: Owning object.
        id: Value reported by ``Menu.item_triggered``; defaults to ``text``.
        icon: Icon name.
        shortcut: Shortcut text such as ``"Ctrl+S"``.
        checkable: Toggle behavior.
        checked: Initial checked state.
        disabled: Start disabled.
        danger: Use the error color for the icon of a destructive action.
    """

    def __init__(self, text: str, parent=None, *, id: str | None = None, icon: str | None = None,  # noqa: A002
                 shortcut: str | None = None, checkable: bool = False, checked: bool = False,
                 disabled: bool = False, danger: bool = False) -> None:
        super().__init__(text, parent)
        self.item_id = id or text
        self.icon_name = icon
        self.danger = danger
        if shortcut:
            self.setShortcut(shortcut)
        self.setCheckable(checkable)
        self.setChecked(checked)
        self.setDisabled(disabled)
        self.refresh_icon()

    def refresh_icon(self) -> None:
        if self.icon_name:
            self.setIcon(make_icon(self.icon_name, 16, "error" if self.danger else "text-secondary"))


class Menu(ThemedMixin, QMenu):
    """A popup menu.

    Args:
        parent: Parent widget.
        items: A list of ``str``, ``MenuItem``, ``dict`` (``MenuItem`` keyword arguments
            plus ``text``, optional ``items`` for a submenu) or ``None`` for a separator.
        title: Title when used as a submenu.

    Signals:
        item_triggered(str): The id of the chosen entry.
    """

    item_triggered = Signal(str)

    def __init__(self, parent=None, *, items=None, title: str = "") -> None:
        super().__init__(title, parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.bind_theme()
        self.triggered.connect(self._on_triggered)
        for item in items or []:
            self.add_item(item)

    def add_item(self, item):
        """Add one entry in any accepted form and return the created action or submenu."""
        if item is None:
            return self.addSeparator()
        if isinstance(item, MenuItem):
            item.setParent(self)
            self.addAction(item)
            return item
        if isinstance(item, str):
            item = {"text": item}
        spec = dict(item)
        text = spec.pop("text")
        children = spec.pop("items", None)
        if children is not None:
            submenu = Menu(self, items=children, title=text)
            submenu.item_triggered.connect(self.item_triggered)
            self.addMenu(submenu)
            return submenu
        action = MenuItem(text, self, **spec)
        self.addAction(action)
        return action

    def refresh_theme(self) -> None:
        for action in self.actions():
            if isinstance(action, MenuItem):
                action.refresh_icon()

    def _on_triggered(self, action) -> None:
        if isinstance(action, MenuItem) and action.parent() is self:
            self.item_triggered.emit(action.item_id)


class DropdownMenu(Button):
    """A button that opens a :class:`Menu`.

    Args:
        text: Button label.
        items: Menu entries.

    Signals:
        item_triggered(str): The id of the chosen entry.
    """

    item_triggered = Signal(str)

    def __init__(self, text: str = "", parent=None, *, items=None, **kwargs) -> None:
        super().__init__(text, parent, **kwargs)
        self.menu_widget = Menu(self, items=items)
        self.menu_widget.item_triggered.connect(self.item_triggered)
        self.setMenu(self.menu_widget)
