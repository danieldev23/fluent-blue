"""Model behind ``DataTable``. It has one pipeline: filter, sort, then page.

Rows stay in their original list. The model serves a ``view`` of source indices, so
sorting and filtering 100,000 rows only reorders integers and never copies row data.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ...compatibility.qt import QAbstractTableModel, QModelIndex, Qt, Signal

CellPainter = Callable[..., None]


@dataclass
class Column:
    """Describes one table column.

    Attributes:
        key: Key of the value in each row dict.
        title: Header text; defaults to the key in title case.
        width: Initial width in pixels; ``None`` leaves it to the table.
        sortable: Allow sorting by this column.
        filterable: Offer this column's values in the filter menu.
        visible: Initially visible.
        align: ``left``, ``center`` or ``right``.
        formatter: ``callable(value) -> str`` for the display text.
        renderer: ``callable(painter, rect, value, row)`` for custom painting.
        sort_key: ``callable(value)`` to override the sort value.
    """

    key: str
    title: str = ""
    width: int | None = None
    sortable: bool = True
    filterable: bool = False
    visible: bool = True
    align: str = "left"
    formatter: Callable[[Any], str] | None = None
    renderer: CellPainter | None = field(default=None, repr=False)
    sort_key: Callable[[Any], Any] | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.title = self.title or self.key.replace("_", " ").title()

    def text(self, value: Any) -> str:
        if self.formatter:
            return self.formatter(value)
        return "" if value is None else str(value)


_ALIGN = {
    "left": Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
    "center": Qt.AlignmentFlag.AlignCenter,
    "right": Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
}
RowRole = Qt.ItemDataRole.UserRole + 1
ValueRole = Qt.ItemDataRole.UserRole + 2


def _sort_token(value: Any) -> tuple:
    # None sorts last, and mixed types compare by type name instead of raising TypeError.
    if value is None:
        return (2, "", 0)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (0, "", value)
    return (1, type(value).__name__, str(value).lower() if isinstance(value, str) else value)


class DataTableModel(QAbstractTableModel):
    """Serves rows after filter, sort and page.

    Signals:
        view_changed: The set of visible rows changed.
    """

    view_changed = Signal()

    def __init__(self, columns, rows=None, parent=None, *, page_size: int | None = None) -> None:
        super().__init__(parent)
        self.columns: list[Column] = [c if isinstance(c, Column) else Column(c) for c in columns]
        self.rows: list[dict] = list(rows or [])
        self.page_size, self.page = page_size, 1
        self.search = ""
        self.column_filters: dict[str, object] = {}
        self.sort_column: int | None = None
        self.sort_order = Qt.SortOrder.AscendingOrder
        self._filtered: list[int] = []
        self._view: list[int] = []
        self._recompute()

    # ---- Qt model API ------------------------------------------------------------
    def rowCount(self, parent=QModelIndex()) -> int:  # noqa: N802, B008 - Qt API
        return 0 if parent.isValid() else len(self._view)

    def columnCount(self, parent=QModelIndex()) -> int:  # noqa: N802, B008 - Qt API
        return 0 if parent.isValid() else len(self.columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        column = self.columns[index.column()]
        row = self.rows[self._view[index.row()]]
        value = row.get(column.key)
        if role == Qt.ItemDataRole.DisplayRole:
            return "" if column.renderer else column.text(value)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(_ALIGN[column.align].value)
        if role == Qt.ItemDataRole.ToolTipRole:
            return column.text(value) if not column.renderer else None
        if role == RowRole:
            return row
        if role == ValueRole:
            return value
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802 - Qt API
        if orientation == Qt.Orientation.Horizontal:
            if role == Qt.ItemDataRole.DisplayRole:
                return self.columns[section].title
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return int(_ALIGN[self.columns[section].align].value)
        return None

    def sort(self, column: int, order=Qt.SortOrder.AscendingOrder) -> None:
        if column < 0 or not self.columns[column].sortable:
            return
        self.sort_column, self.sort_order = column, order
        self._rebuild()

    # ---- data API ----------------------------------------------------------------
    def set_rows(self, rows) -> None:
        """Replace all rows and return to page 1."""
        self.rows = list(rows)
        self.page = 1
        self._rebuild()

    def source_index(self, view_row: int) -> int:
        """Map a visible row to its index in :attr:`rows`."""
        return self._view[view_row]

    def view_row(self, source_index: int) -> int | None:
        """Map a source index to its visible row, or ``None`` if not on this page."""
        try:
            return self._view.index(source_index)
        except ValueError:
            return None

    def filtered_count(self) -> int:
        """Rows matching the filters, across all pages."""
        return len(self._filtered)

    def filtered_rows(self) -> list[dict]:
        """Rows matching the filters, in sorted order, across all pages."""
        return [self.rows[i] for i in self._filtered]

    def set_search(self, text: str) -> None:
        """Filter rows by a case-insensitive match across visible text."""
        self.search = text.strip().lower()
        self.page = 1
        self._rebuild()

    def set_column_filter(self, key: str, condition) -> None:
        """Filter one column.

        Args:
            key: Column key.
            condition: A collection of allowed values, a ``callable(value) -> bool``,
                or ``None`` to clear the filter.
        """
        if condition is None:
            self.column_filters.pop(key, None)
        else:
            self.column_filters[key] = condition
        self.page = 1
        self._rebuild()

    def set_page(self, page: int) -> None:
        self.page = max(1, page)
        self._rebuild()

    def set_page_size(self, size: int | None) -> None:
        self.page_size = size
        self.page = 1
        self._rebuild()

    def distinct_values(self, key: str) -> list:
        """Sorted distinct values of a column, for filter menus."""
        return sorted({row.get(key) for row in self.rows}, key=_sort_token)

    # ---- pipeline -----------------------------------------------------------------
    def _rebuild(self) -> None:
        self.layoutAboutToBeChanged.emit()
        self.beginResetModel()
        self._recompute()
        self.endResetModel()
        self.layoutChanged.emit()
        self.view_changed.emit()

    def _matches(self, row: dict) -> bool:
        for key, condition in self.column_filters.items():
            value = row.get(key)
            if callable(condition):
                if not condition(value):
                    return False
            elif value not in condition:
                return False
        if self.search:
            return any(self.search in c.text(row.get(c.key)).lower() for c in self.columns)
        return True

    def _recompute(self) -> None:
        if self.search or self.column_filters:
            indices = [i for i, row in enumerate(self.rows) if self._matches(row)]
        else:
            indices = list(range(len(self.rows)))
        if self.sort_column is not None:
            column = self.columns[self.sort_column]
            convert = column.sort_key or (lambda value: value)
            rows, key = self.rows, column.key
            indices.sort(key=lambda i: _sort_token(convert(rows[i].get(key))),
                         reverse=self.sort_order == Qt.SortOrder.DescendingOrder)
        self._filtered = indices
        if self.page_size:
            pages = max(1, (len(indices) + self.page_size - 1) // self.page_size)
            self.page = min(self.page, pages)
            start = (self.page - 1) * self.page_size
            self._view = indices[start:start + self.page_size]
        else:
            self._view = indices
