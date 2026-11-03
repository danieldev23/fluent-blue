"""A button with a primary action and a menu of alternatives."""
from __future__ import annotations

from ...compatibility.qt import QHBoxLayout, QPoint, QSizePolicy, QWidget, Signal
from ..navigation.menu import Menu
from .button import Button


class SplitButton(QWidget):
    """Primary action on the left, a menu of related actions on the right.

    Args:
        text: Label of the main action.
        items: Menu entries, accepted in every form :class:`Menu` understands.
        variant: Button variant applied to both parts.
        size: ``small``, ``medium`` or ``large``.
        icon: Icon of the main action.
        disabled: Start disabled.

    Signals:
        clicked: The main action was activated.
        item_triggered(str): A menu entry was chosen; carries its id.
    """

    clicked = Signal()
    item_triggered = Signal(str)

    def __init__(self, text: str = "", parent=None, *, items=None, variant: str = "primary", size: str = "medium",
                 icon=None, disabled: bool = False) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.main_button = Button(text, variant=variant, size=size, icon=icon)
        self.main_button.setProperty("splitPart", "main")
        self.arrow_button = Button("", variant=variant, size=size, icon="chevron-down", tooltip="More actions")
        self.arrow_button.setProperty("splitPart", "arrow")
        self.arrow_button.setAccessibleName(f"{text}: more actions")
        self.menu = Menu(self, items=items)
        self.menu.item_triggered.connect(self.item_triggered)
        layout.addWidget(self.main_button)
        layout.addWidget(self.arrow_button)
        self.main_button.clicked.connect(lambda: self.clicked.emit())
        self.arrow_button.clicked.connect(self.show_menu)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setDisabled(disabled)

    def show_menu(self) -> None:
        """Open the menu below the control."""
        self.menu.popup(self.mapToGlobal(QPoint(0, self.height() + 4)))
