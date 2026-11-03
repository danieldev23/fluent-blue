"""DataTable: a complete table built on Qt's model/view framework."""
from __future__ import annotations

import csv
import json

from ...compatibility.qt import (
    QAbstractItemView, QApplication, QFileDialog, QFrame, QHBoxLayout, QHeaderView, QPainter, QRectF, QSize,
    QStackedLayout, QStyle, QStyledItemDelegate, QStyleOptionViewItem, Qt, QTableView, QVBoxLayout, QWidget, Signal,
)
from ...core.theme_manager import ThemeManager
from ..base import check_choice
from ..buttons.button import Button
from ..display.content import EmptyState
from ..feedback.feedback import LoadingOverlay
from ..inputs.input import SearchInput
from ..navigation.menu import Menu, MenuItem
from ..navigation.wayfinding import Pagination
from .model import DataTableModel, RowRole, ValueRole

_SELECTION = {
    "none": QAbstractItemView.SelectionMode.NoSelection,
    "single": QAbstractItemView.SelectionMode.SingleSelection,
    "multi": QAbstractItemView.SelectionMode.ExtendedSelection,
}


def badge_renderer(variants: dict | None = None, default: str = "neutral"):
    """Cell renderer that draws the value as a pill. ``variants`` maps values to variants."""
    variants = variants or {}

    def render(painter: QPainter, rect, value, _row) -> None:
        name = variants.get(value, default)
        bg = {"neutral": "surface-tertiary", "primary": "primary-subtle"}.get(name, f"{name}-subtle")
        fg = {"neutral": "text-secondary", "primary": "primary-text"}.get(name, f"{name}-text")
        text = "" if value is None else str(value)
        painter.setFont(ThemeManager.font("caption"))
        width = painter.fontMetrics().horizontalAdvance(text) + 16
        pill = QRectF(rect.left() + 10, rect.center().y() - 9 + 1, width, 18)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor(bg))
        painter.drawRoundedRect(pill, 9, 9)
        painter.setPen(ThemeManager.qcolor(fg))
        painter.drawText(pill, Qt.AlignmentFlag.AlignCenter, text)

    return render


def progress_renderer(maximum: float = 100, variant: str = "primary"):
    """Cell renderer that draws a numeric value as a small bar."""

    def render(painter: QPainter, rect, value, _row) -> None:
        fraction = min(1.0, max(0.0, float(value or 0) / maximum))
        track = QRectF(rect.left() + 10, rect.center().y() - 2, rect.width() - 52, 5)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(ThemeManager.qcolor("surface-tertiary"))
        painter.drawRoundedRect(track, 2.5, 2.5)
        painter.setBrush(ThemeManager.qcolor(variant))
        painter.drawRoundedRect(QRectF(track.left(), track.top(), track.width() * fraction, 5), 2.5, 2.5)
        painter.setPen(ThemeManager.qcolor("text-secondary"))
        painter.setFont(ThemeManager.font("caption"))
        area = QRectF(track.right() + 4, rect.top(), 34, rect.height())
        painter.drawText(area, int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter), f"{round(fraction * 100)}%")

    return render


class _Delegate(QStyledItemDelegate):
    """Paints the hover or selection background, then the custom renderer."""

    def __init__(self, table) -> None:
        super().__init__(table)
        self._table = table

    def paint(self, painter, option, index) -> None:
        column = self._table.model.columns[index.column()]
        if column.renderer is None:
            super().paint(painter, option, index)
            return
        style = QStyleOptionViewItem(option)
        self.initStyleOption(style, index)
        style.text = ""
        widget = style.widget
        (widget.style() if widget else QApplication.style()).drawControl(QStyle.ControlElement.CE_ItemViewItem, style, painter, widget)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        column.renderer(painter, option.rect, index.data(ValueRole), index.data(RowRole))
        painter.restore()


class DataTable(QFrame):
    """A table with sorting, filtering, paging, selection, column control and export.

    Args:
        columns: :class:`Column` objects or plain keys.
        rows: A list of dicts.
        page_size: Rows per page; ``None`` disables paging and shows all rows.
        selection: ``none``, ``single`` or ``multi``. Selection persists across pages.
        searchable: Show the search field.
        column_menu: Show the column visibility button.
        exportable: Show the export button.
        striped: Alternate row backgrounds.
        empty_title: Headline of the empty state.
        empty_description: Text of the empty state.
        row_height: Row height in pixels.

    Signals:
        selection_changed(list): The selected row dicts.
        row_activated(dict): A row was double-clicked or Enter was pressed.
        page_changed(int): The current page changed.
        context_menu_requested(list, object): Rows under the cursor and the global position.
    """

    selection_changed = Signal(list)
    row_activated = Signal(dict)
    page_changed = Signal(int)
    context_menu_requested = Signal(list, object)

    def __init__(self, columns=None, rows=None, parent=None, *, page_size: int | None = 25, selection: str = "single",
                 searchable: bool = True, column_menu: bool = True, exportable: bool = True, striped: bool = False,
                 empty_title: str = "No results", empty_description: str = "Try changing the search or filters.",
                 row_height: int = 36) -> None:
        super().__init__(parent)
        check_choice("selection", selection, _SELECTION)
        ThemeManager.ensure_applied()
        self.model = DataTableModel(columns or [], rows, self, page_size=page_size)
        self._selected: set[int] = set()
        self._restoring = False
        self._loading = False
        self.context_menu_factory = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.toolbar = QFrame()
        self.toolbar.setObjectName("toolbar")
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(8, 8, 8, 8)
        self.toolbar_layout.setSpacing(8)
        self.search = None
        if searchable:
            self.search = SearchInput(size="small")
            self.search.setMaximumWidth(280)
            self.search.search_changed.connect(self.model.set_search)
            self.toolbar_layout.addWidget(self.search, 1)
        self.toolbar_layout.addStretch(1)
        self.filter_button = None
        if any(c.filterable for c in self.model.columns):
            self.filter_button = Button("Filter", size="small", icon="filter", variant="ghost")
            self.filter_button.clicked.connect(self._show_filter_menu)
            self.toolbar_layout.addWidget(self.filter_button)
        if column_menu:
            button = Button("Columns", size="small", icon="columns", variant="ghost")
            button.clicked.connect(lambda: self._show_column_menu(button))
            self.toolbar_layout.addWidget(button)
        if exportable:
            button = Button("Export", size="small", icon="download", variant="ghost")
            button.clicked.connect(self._export_dialog)
            self.toolbar_layout.addWidget(button)
        self.toolbar.setVisible(self.toolbar_layout.count() > 1)
        layout.addWidget(self.toolbar)
        self._holder = QWidget()
        self._stack = QStackedLayout(self._holder)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setItemDelegate(_Delegate(self))
        self.view.setSortingEnabled(True)
        self.view.setShowGrid(False)
        self.view.setAlternatingRowColors(striped)
        self.view.setWordWrap(False)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setSelectionMode(_SELECTION[selection])
        self.view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._context_menu)
        self.view.activated.connect(self._on_activated)
        self.view.setMouseTracking(True)
        self.view.setAccessibleName("Data table")
        vertical = self.view.verticalHeader()
        vertical.setVisible(False)
        vertical.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        vertical.setDefaultSectionSize(row_height)
        header = self.view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        header.setHighlightSections(False)
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        header.setMinimumSectionSize(48)
        header.setDefaultSectionSize(140)
        self._apply_columns()
        self.view.selectionModel().selectionChanged.connect(self._on_selection)
        self._stack.addWidget(self.view)
        self._empty_text = (empty_title, empty_description)
        self._empty_state = None
        layout.addWidget(self._holder, 1)
        self.footer = QFrame()
        self.footer.setObjectName("footer")
        footer = QHBoxLayout(self.footer)
        footer.setContentsMargins(12, 6, 8, 6)
        self.pagination = None
        if page_size:
            self.pagination = Pagination(total=self.model.filtered_count(), page_size=page_size)
            self.pagination.page_changed.connect(self._on_page)
            footer.addWidget(self.pagination)
        self.footer.setVisible(bool(page_size))
        layout.addWidget(self.footer)
        self._overlay = None
        self.model.view_changed.connect(self._on_view_changed)
        self._on_view_changed()

    @property
    def empty_state(self) -> EmptyState:
        """The empty state, created the first time it is needed."""
        if self._empty_state is None:
            title, description = self._empty_text
            self._empty_state = EmptyState(title, description=description, icon="search")
            self._stack.addWidget(self._empty_state)
        return self._empty_state

    @property
    def overlay(self) -> LoadingOverlay:
        """The loading overlay, created the first time it is needed."""
        if self._overlay is None:
            self._overlay = LoadingOverlay(self._holder)
        return self._overlay

    # ---- data ------------------------------------------------------------------------
    def rows(self) -> list[dict]:
        return self.model.rows

    def set_rows(self, rows) -> None:
        """Replace the rows and clear the selection."""
        self._selected.clear()
        self.model.set_rows(rows)
        self.selection_changed.emit([])

    def set_loading(self, loading: bool, message: str = "Loading…") -> None:
        """Show or hide the loading overlay."""
        self._loading = loading
        if loading:
            self.overlay.start(message)
        elif self._overlay is not None:
            self._overlay.stop()

    def is_loading(self) -> bool:
        return self._loading

    def visible_row_count(self) -> int:
        """Rows on the current page."""
        return self.model.rowCount()

    # ---- sort and filter ---------------------------------------------------------------
    def sort_by(self, key: str, descending: bool = False) -> None:
        """Sort by a column key."""
        order = Qt.SortOrder.DescendingOrder if descending else Qt.SortOrder.AscendingOrder
        self.view.horizontalHeader().setSortIndicator(self._column_index(key), order)

    def set_search(self, text: str) -> None:
        """Set the global search; this also updates the search field."""
        if self.search:
            self.search.blockSignals(True)
            self.search.setText(text)
            self.search.blockSignals(False)
        self.model.set_search(text)

    def set_column_filter(self, key: str, condition) -> None:
        """Filter a column; see :meth:`DataTableModel.set_column_filter`."""
        self._column_index(key)
        self.model.set_column_filter(key, condition)

    def clear_filters(self) -> None:
        self.model.column_filters.clear()
        self.set_search("")

    # ---- columns -------------------------------------------------------------------------
    def set_column_visible(self, key: str, visible: bool) -> None:
        self.view.setColumnHidden(self._column_index(key), not visible)
        self.model.columns[self._column_index(key)].visible = visible

    def is_column_visible(self, key: str) -> bool:
        return not self.view.isColumnHidden(self._column_index(key))

    # ---- selection ------------------------------------------------------------------------
    def selected_rows(self) -> list[dict]:
        """Selected rows across all pages, in source order."""
        return [self.model.rows[i] for i in sorted(self._selected)]

    def select_rows(self, source_indices) -> None:
        """Replace the selection using indices into the row list."""
        self._selected = {i for i in source_indices if 0 <= i < len(self.model.rows)}
        self._restore_selection()
        self.selection_changed.emit(self.selected_rows())

    def clear_selection(self) -> None:
        self.select_rows([])

    # ---- paging ---------------------------------------------------------------------------
    def page(self) -> int:
        return self.model.page

    def set_page(self, page: int) -> None:
        if self.pagination is not None:
            self.pagination.set_page(page)

    # ---- export ---------------------------------------------------------------------------
    def export_csv(self, path, *, all_rows: bool = True) -> int:
        """Write rows to CSV using visible columns and return the row count.

        Args:
            path: Destination file.
            all_rows: ``True`` for every filtered row; ``False`` for the current page.
        """
        columns = [c for c in self.model.columns if self.is_column_visible(c.key)]
        rows = self.model.filtered_rows() if all_rows else [self.model.rows[i] for i in self.model._view]
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([c.title for c in columns])
            for row in rows:
                writer.writerow([c.text(row.get(c.key)) for c in columns])
        return len(rows)

    def export_json(self, path, *, all_rows: bool = True) -> int:
        """Write rows to JSON using visible columns and return the row count."""
        columns = [c for c in self.model.columns if self.is_column_visible(c.key)]
        rows = self.model.filtered_rows() if all_rows else [self.model.rows[i] for i in self.model._view]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump([{c.key: row.get(c.key) for c in columns} for row in rows], handle, ensure_ascii=False, indent=2, default=str)
        return len(rows)

    # ---- internals --------------------------------------------------------------------------
    def _column_index(self, key: str) -> int:
        for index, column in enumerate(self.model.columns):
            if column.key == key:
                return index
        raise KeyError(f"Unknown column: {key!r}")

    def _apply_columns(self) -> None:
        for index, column in enumerate(self.model.columns):
            if column.width:
                self.view.setColumnWidth(index, column.width)
            self.view.setColumnHidden(index, not column.visible)

    def _on_view_changed(self) -> None:
        total = self.model.filtered_count()
        if self.pagination is not None:
            self.pagination.set_total(total)
        if total == 0:
            self._stack.setCurrentWidget(self.empty_state)
        else:
            self._stack.setCurrentWidget(self.view)
        self._restore_selection()

    def _on_page(self, page: int) -> None:
        self.model.set_page(page)
        self.view.scrollToTop()
        self.page_changed.emit(page)

    def _on_activated(self, index) -> None:
        self.row_activated.emit(self.model.rows[self.model.source_index(index.row())])

    def _on_selection(self, selected, deselected) -> None:
        if self._restoring:
            return
        for index in deselected.indexes():
            if index.row() < self.model.rowCount():
                self._selected.discard(self.model.source_index(index.row()))
        added = {self.model.source_index(i.row()) for i in selected.indexes()}
        if self.view.selectionMode() == QAbstractItemView.SelectionMode.SingleSelection and added:
            self._selected = added
        else:
            self._selected |= added
        self.selection_changed.emit(self.selected_rows())

    def _restore_selection(self) -> None:
        self._restoring = True
        model = self.view.selectionModel()
        model.clearSelection()
        flags = model.SelectionFlag.Select | model.SelectionFlag.Rows
        for source in self._selected:
            row = self.model.view_row(source)
            if row is not None:
                model.select(self.model.index(row, 0), flags)
        self._restoring = False

    def _show_column_menu(self, anchor) -> None:
        menu = Menu(self)
        for column in self.model.columns:
            action = MenuItem(column.title, menu, id=column.key, checkable=True, checked=self.is_column_visible(column.key))
            action.toggled.connect(lambda on, key=column.key: self.set_column_visible(key, on))
            menu.add_item(action)
        menu.popup(anchor.mapToGlobal(anchor.rect().bottomLeft()))

    def _show_filter_menu(self) -> None:
        menu = Menu(self)
        for column in self.model.columns:
            if not column.filterable:
                continue
            submenu = Menu(menu, title=column.title)
            active = self.model.column_filters.get(column.key)
            for value in self.model.distinct_values(column.key):
                action = MenuItem(column.text(value), submenu, id=str(value), checkable=True,
                                  checked=active is not None and value in active)
                action.toggled.connect(lambda on, key=column.key, v=value: self._toggle_filter(key, v, on))
                submenu.add_item(action)
            menu.addMenu(submenu)
        menu.addSeparator()
        clear = menu.add_item({"text": "Clear filters", "icon": "close"})
        clear.triggered.connect(self.clear_filters)
        button = self.filter_button
        menu.popup(button.mapToGlobal(button.rect().bottomLeft()))

    def _toggle_filter(self, key: str, value, on: bool) -> None:
        allowed = set(self.model.column_filters.get(key) or ())
        allowed.add(value) if on else allowed.discard(value)
        self.model.set_column_filter(key, allowed or None)

    def _context_menu(self, position) -> None:
        index = self.view.indexAt(position)
        if index.isValid() and self.model.source_index(index.row()) not in self._selected:
            self.select_rows([self.model.source_index(index.row())])
        rows = self.selected_rows()
        target = self.view.viewport().mapToGlobal(position)
        self.context_menu_requested.emit(rows, target)
        factory = self.context_menu_factory
        menu = factory(rows) if factory else self._default_menu(rows)
        if menu is not None:
            menu.popup(target)

    def _default_menu(self, rows):
        if not rows:
            return None
        menu = Menu(self)
        menu.add_item({"text": "Copy row" if len(rows) == 1 else f"Copy {len(rows)} rows", "icon": "copy"}).triggered.connect(lambda: self.copy_rows(rows))
        return menu

    def copy_rows(self, rows) -> None:
        """Copy rows to the clipboard as tab-separated text."""
        columns = [c for c in self.model.columns if self.is_column_visible(c.key)]
        lines = ["\t".join(c.text(row.get(c.key)) for c in columns) for row in rows]
        QApplication.clipboard().setText("\n".join(lines))

    def _export_dialog(self) -> None:
        path, chosen = QFileDialog.getSaveFileName(self, "Export table", "export.csv", "CSV (*.csv);;JSON (*.json)")
        if path:
            (self.export_json if path.endswith(".json") or "JSON" in chosen else self.export_csv)(path)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(640, 420)

