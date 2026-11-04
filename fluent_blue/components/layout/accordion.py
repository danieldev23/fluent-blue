"""Accordion: a stack of collapsible sections."""
from __future__ import annotations

from ...compatibility.qt import QVBoxLayout, QWidget, Signal
from ...core.theme_manager import ThemeManager
from .containers import CollapsiblePanel


class Accordion(QWidget):
    """A vertical stack of collapsible sections, optionally allowing only one open at a time.

    Args:
        exclusive: Opening a section closes the others.
        spacing: Spacing token step between sections.

    Signals:
        expanded_changed(int, bool): The index of a section and whether it is now expanded.
    """

    expanded_changed = Signal(int, bool)

    def __init__(self, parent=None, *, exclusive: bool = False, spacing: int = 2) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        self._exclusive = exclusive
        self._items: list[CollapsiblePanel] = []
        self._syncing = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(ThemeManager.spacing(spacing))
        self._layout = layout
        layout.addStretch(1)

    def add_item(self, title: str, content, *, expanded: bool = False) -> CollapsiblePanel:
        """Add a section holding ``content`` (a widget, or text) and return its panel."""
        from ..display.text import Text

        panel = CollapsiblePanel(title, expanded=expanded)
        panel.add(Text(content, color="text-secondary", wrap=True) if isinstance(content, str) else content)
        index = len(self._items)
        self._items.append(panel)
        panel.toggled.connect(lambda on, i=index: self._on_toggled(i, on))
        self._layout.insertWidget(self._layout.count() - 1, panel)
        if expanded and self._exclusive:
            self._collapse_others(index)
        return panel

    def count(self) -> int:
        return len(self._items)

    def is_expanded(self, index: int) -> bool:
        return self._items[index].is_expanded()

    def set_expanded(self, index: int, expanded: bool) -> None:
        """Expand or collapse a section; in exclusive mode opening one closes the rest."""
        self._items[index].set_expanded(expanded)

    def expand_all(self) -> None:
        """Open every section. Ignored in exclusive mode."""
        if not self._exclusive:
            for panel in self._items:
                panel.set_expanded(True)

    def collapse_all(self) -> None:
        for panel in self._items:
            panel.set_expanded(False)

    def _collapse_others(self, keep: int) -> None:
        self._syncing = True
        try:
            for index, panel in enumerate(self._items):
                if index != keep and panel.is_expanded():
                    panel.set_expanded(False)
                    self.expanded_changed.emit(index, False)
        finally:
            self._syncing = False

    def _on_toggled(self, index: int, expanded: bool) -> None:
        if self._syncing:
            return
        if expanded and self._exclusive:
            self._collapse_others(index)
        self.expanded_changed.emit(index, expanded)
