"""Container, Stack, Grid, Splitter, Panel, CollapsiblePanel, ScrollArea."""
from __future__ import annotations

from ...compatibility.qt import (
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QSize,
    QSizePolicy,
    QSplitter,
    Qt,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.animations import animate
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ..base import ThemedMixin, check_choice
from ..display.text import Text


class Container(QWidget):
    """Centers content and limits its width, keeping long lines readable on wide screens.

    Args:
        max_width: Maximum content width in pixels.
        padding: Spacing token step used around the content.
    """

    def __init__(self, parent=None, *, max_width: int = 1120, padding: int = 6) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        outer = QHBoxLayout(self)
        p = ThemeManager.spacing(padding)
        outer.setContentsMargins(p, p, p, p)
        self.content = QWidget()
        self.content.setMaximumWidth(max_width)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(ThemeManager.spacing(4))
        outer.addStretch(0)
        outer.addWidget(self.content, 1)
        outer.addStretch(0)

    def add(self, widget, stretch: int = 0):
        """Add a widget to the content and return it."""
        self.content_layout.addWidget(widget, stretch)
        return widget


class Stack(QWidget):
    """Arranges children in a row or column with token spacing.

    Args:
        children: Initial widgets.
        direction: ``vertical`` or ``horizontal``.
        spacing: Spacing token step (2 means 8 px).
        padding: Spacing token step around the content.
        align: ``start``, ``center``, ``end`` or ``stretch`` on the cross axis.
    """

    def __init__(self, children=None, parent=None, *, direction: str = "vertical", spacing: int = 2, padding: int = 0,
                 align: str = "stretch") -> None:
        super().__init__(parent)
        check_choice("direction", direction, ("vertical", "horizontal"))
        check_choice("align", align, ("start", "center", "end", "stretch"))
        ThemeManager.ensure_applied()
        vertical = direction == "vertical"
        self._align = {
            "stretch": Qt.AlignmentFlag(0),
            "start": Qt.AlignmentFlag.AlignLeft if vertical else Qt.AlignmentFlag.AlignTop,
            "center": Qt.AlignmentFlag.AlignHCenter if vertical else Qt.AlignmentFlag.AlignVCenter,
            "end": Qt.AlignmentFlag.AlignRight if vertical else Qt.AlignmentFlag.AlignBottom,
        }[align]
        self._box = QBoxLayout(QBoxLayout.Direction.TopToBottom if vertical else QBoxLayout.Direction.LeftToRight, self)
        p = ThemeManager.spacing(padding)
        self._box.setContentsMargins(p, p, p, p)
        self._box.setSpacing(ThemeManager.spacing(spacing))
        self._horizontal = not vertical
        if self._horizontal:
            # A zero-stretch spacer packs fixed-size children to the start, while expanding
            # children still share the free width.
            self._box.addStretch(0)
        for child in children or []:
            self.add(child)

    def add(self, widget, stretch: int = 0):
        """Add a widget and return it."""
        position = self._box.count() - 1 if self._horizontal else self._box.count()
        self._box.insertWidget(position, widget, stretch, self._align)
        return widget

    def add_stretch(self, stretch: int = 1) -> None:
        """Add flexible empty space."""
        position = self._box.count() - 1 if self._horizontal else self._box.count()
        self._box.insertStretch(position, stretch)

    def add_spacing(self, step: int) -> None:
        """Add fixed space by token step."""
        position = self._box.count() - 1 if self._horizontal else self._box.count()
        self._box.insertSpacing(position, ThemeManager.spacing(step))


class Grid(QWidget):
    """A grid with a fixed column count, or responsive columns from a minimum width.

    Args:
        columns: Fixed column count. Ignored if ``min_column_width`` is set.
        min_column_width: Reflow to fit as many columns of this width as possible.
        gap: Spacing token step between cells.
    """

    def __init__(self, parent=None, *, columns: int = 3, min_column_width: int | None = None, gap: int = 3) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        self._columns, self._min_width = max(1, columns), min_column_width
        self._items: list[tuple] = []
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._gap = ThemeManager.spacing(gap)
        self._grid.setSpacing(self._gap)
        self._current_columns = self._columns

    def add(self, widget, col_span: int = 1):
        """Add a widget spanning ``col_span`` columns and return it."""
        self._items.append((widget, col_span))
        self._relayout()
        return widget

    def column_count(self) -> int:
        return self._current_columns

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        if self._min_width:
            columns = max(1, (self.width() + self._gap) // (self._min_width + self._gap))
            if columns != self._current_columns:
                self._current_columns = columns
                self._relayout()

    def _relayout(self) -> None:
        for widget, _span in self._items:
            self._grid.removeWidget(widget)
        columns = self._current_columns
        row = column = 0
        for widget, span in self._items:
            span = min(span, columns)
            if column + span > columns:
                row, column = row + 1, 0
            self._grid.addWidget(widget, row, column, 1, span)
            column += span
        for index in range(max(columns, self._grid.columnCount())):
            self._grid.setColumnStretch(index, 1 if index < columns else 0)


class Splitter(QSplitter):
    """A resizable split view.

    Args:
        widgets: Initial panes.
        orientation: ``horizontal`` or ``vertical``.
        sizes: Initial pane sizes in pixels.
        collapsible: Allow panes to be collapsed by dragging.

    Signals:
        Inherits ``splitterMoved(int, int)`` from ``QSplitter``.
    """

    def __init__(self, widgets=None, parent=None, *, orientation: str = "horizontal", sizes=None, collapsible: bool = False) -> None:
        check_choice("orientation", orientation, ("horizontal", "vertical"))
        super().__init__(Qt.Orientation.Horizontal if orientation == "horizontal" else Qt.Orientation.Vertical, parent)
        ThemeManager.ensure_applied()
        self.setChildrenCollapsible(collapsible)
        self.setHandleWidth(1)
        for widget in widgets or []:
            self.addWidget(widget)
        if sizes:
            self.setSizes(list(sizes))


class Panel(QFrame):
    """A titled section with a header action area.

    Args:
        title: Header title.
        actions: Widgets placed at the right of the header.
        padding: Spacing token step around the body.
    """

    def __init__(self, title: str = "", parent=None, *, actions=None, padding: int = 4) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if title or actions:
            header = QFrame()
            header.setObjectName("panelHeader")
            row = QHBoxLayout(header)
            row.setContentsMargins(12, 8, 8, 8)
            row.addWidget(Text(title, style="heading-5"))
            row.addStretch(1)
            for action in actions or []:
                row.addWidget(action)
            layout.addWidget(header)
        holder = QWidget()
        self.body = QVBoxLayout(holder)
        p = ThemeManager.spacing(padding)
        self.body.setContentsMargins(p, p, p, p)
        self.body.setSpacing(ThemeManager.spacing(2))
        layout.addWidget(holder, 1)

    def add(self, widget, stretch: int = 0):
        """Add a widget to the body and return it."""
        self.body.addWidget(widget, stretch)
        return widget


class CollapsiblePanel(ThemedMixin, QFrame):
    """A panel whose content expands and collapses.

    Args:
        title: Header text.
        expanded: Initial state.
        padding: Spacing token step around the body.

    Signals:
        toggled(bool): ``True`` when expanded.
    """

    toggled = Signal(bool)

    def __init__(self, title: str = "", parent=None, *, expanded: bool = True, padding: int = 3) -> None:
        super().__init__(parent)
        self._expanded = expanded
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.header = QPushButton(title)
        self.header.setObjectName("panelToggle")
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.header.setIconSize(QSize(14, 14))
        self.header.clicked.connect(self.toggle)
        layout.addWidget(self.header)
        self.content = QWidget()
        self.body = QVBoxLayout(self.content)
        p = ThemeManager.spacing(padding)
        self.body.setContentsMargins(p, 0, p, p)
        self.body.setSpacing(ThemeManager.spacing(2))
        layout.addWidget(self.content)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.bind_theme()
        self.refresh_theme()
        self.content.setVisible(expanded)
        self.header.setAccessibleDescription("Expanded" if expanded else "Collapsed")

    def add(self, widget, stretch: int = 0):
        """Add a widget to the body and return it."""
        self.body.addWidget(widget, stretch)
        return widget

    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool) -> None:
        """Expand or collapse with an animation."""
        if expanded == self._expanded:
            return
        self._expanded = expanded
        self.refresh_theme()
        self.header.setAccessibleDescription("Expanded" if expanded else "Collapsed")
        height = self.content.sizeHint().height()
        if expanded:
            self.content.setMaximumHeight(0)
            self.content.setVisible(True)
            animate(self.content, b"maximumHeight", height, start=0,
                    on_finished=lambda: self.content.setMaximumHeight(16777215))
        else:
            animate(self.content, b"maximumHeight", 0, start=height, on_finished=self._finish_collapse)
        self.toggled.emit(expanded)

    def toggle(self) -> None:
        self.set_expanded(not self._expanded)

    def refresh_theme(self) -> None:
        self.header.setIcon(make_icon("chevron-down" if self._expanded else "chevron-right", 14, "text-secondary"))

    def _finish_collapse(self) -> None:
        if not self._expanded:
            self.content.setVisible(False)
            self.content.setMaximumHeight(16777215)


class ScrollArea(QScrollArea):
    """A frameless scroll area with themed scrollbars and a resizable content widget.

    Args:
        widget: Content widget.
        horizontal: Allow horizontal scrolling.
    """

    def __init__(self, widget=None, parent=None, *, horizontal: bool = False) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        if not horizontal:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        if widget is not None:
            self.setWidget(widget)

    def scroll_to_top(self) -> None:
        self.verticalScrollBar().setValue(0)
