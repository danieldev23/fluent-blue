# DataTableModel

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Serves rows after filter, sort and page.

Group: Uncatalogued. Qt base: `QAbstractTableModel`, whose full API stays available.

## Import

```python
from fluent_blue import DataTableModel
```

## Signature

```python
DataTableModel(columns, rows=None, parent=None, page_size=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `columns` | `required` | Column objects or plain keys. |
| `rows` | `None` | A list of dicts. |
| `parent` | `None` | Parent widget. |
| `page_size` | `None` | Rows per page, or None for all. |

## Signals

- `view_changed()`: The set of visible rows changed.

## Public methods

- `data(index, role=<ItemDataRole.DisplayRole: 0>)`
- `distinct_values(key: str) -> list`: Sorted distinct values of a column, for filter menus.
- `filtered_count() -> int`: Rows matching the filters, across all pages.
- `filtered_rows() -> list[dict]`: Rows matching the filters, in sorted order, across all pages.
- `set_column_filter(key: str, condition)`: Filter one column.
- `set_page(page: int)`
- `set_page_size(size: int | None)`
- `set_rows(rows)`: Replace all rows and return to page 1.
- `set_search(text: str)`: Filter rows by a case-insensitive match across visible text.
- `sort(column: int, order=<SortOrder.AscendingOrder: 0>)`
- `source_index(view_row: int) -> int`: Map a visible row to its index in rows.
- `view_row(source_index: int) -> int | None`: Map a source index to its visible row, or None if not on this page.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Never connect a lambda or closure that captures a widget to `ThemeManager` signals: it outlives the widget, and PyQt aborts when it fires. Use `ThemedMixin` or a bound method.
- Keep theme switches fast: do not rebuild child widgets in `refresh_theme()`, and free one-shot menus and dialogs with `WA_DeleteOnClose` or `finished.connect(dialog.deleteLater)`.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
