# DataTable

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A table with sorting, filtering, paging, selection, column control and export.

Group: Data Tables. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import DataTable
```

## Signature

```python
DataTable(columns=None, rows=None, parent=None, page_size=25, selection='single', searchable=True, column_menu=True, exportable=True, striped=False, empty_title='No results', empty_description='Try changing the search or filters.', row_height=36)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `columns` | `None` | Column objects or plain keys. |
| `rows` | `None` | A list of dicts. |
| `parent` | `None` | Parent widget. |
| `page_size` | `25` | Rows per page; None disables paging and shows all rows. |
| `selection` | `'single'` | none, single or multi. Selection persists across pages. |
| `searchable` | `True` | Show the search field. |
| `column_menu` | `True` | Show the column visibility button. |
| `exportable` | `True` | Show the export button. |
| `striped` | `False` | Alternate row backgrounds. |
| `empty_title` | `'No results'` | Headline of the empty state. |
| `empty_description` | `'Try changing the search or filters.'` | Text of the empty state. |
| `row_height` | `36` | Row height in pixels. |

## Signals

- `selection_changed(list)`: The selected row dicts.
- `row_activated(dict)`: A row was double-clicked or Enter was pressed.
- `page_changed(int)`: The current page changed.
- `context_menu_requested(list, object)`: Rows under the cursor and the global position.

## Public methods

- `clear_filters()`
- `clear_selection()`
- `copy_rows(rows)`: Copy rows to the clipboard as tab-separated text.
- `export_csv(path, *, all_rows: bool = True) -> int`: Write rows to CSV using visible columns and return the row count.
- `export_json(path, *, all_rows: bool = True) -> int`: Write rows to JSON using visible columns and return the row count.
- `is_column_visible(key: str) -> bool`
- `is_loading() -> bool`
- `page() -> int`
- `rows() -> list[dict]`
- `select_rows(source_indices)`: Replace the selection using indices into the row list.
- `selected_rows() -> list[dict]`: Selected rows across all pages, in source order.
- `set_column_filter(key: str, condition)`: Filter a column; see set_column_filter.
- `set_column_visible(key: str, visible: bool)`
- `set_loading(loading: bool, message: str = Loading…)`: Show or hide the loading overlay.
- `set_page(page: int)`
- `set_rows(rows)`: Replace the rows and clear the selection.
- `set_search(text: str)`: Set the global search; this also updates the search field.
- `sort_by(key: str, descending: bool = False)`: Sort by a column key.
- `visible_row_count() -> int`: Rows on the current page.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
import random

from fluent_blue import Column, DataTable, badge_renderer, progress_renderer

rng = random.Random(7)
names = ["Atlas", "Borealis", "Cirrus", "Delta", "Echo", "Fable", "Gemini", "Helix", "Ion", "Juno"]
rows = [{
    "id": 1000 + i,
    "project": f"{rng.choice(names)} {rng.randint(1, 99)}",
    "status": rng.choice(["Active", "Paused", "Failed"]),
    "owner": rng.choice(["Ada", "Grace", "Alan", "Katherine"]),
    "progress": rng.randint(4, 100),
    "cost": round(rng.uniform(120, 9800), 2),
} for i in range(240)]

demo = DataTable([
    Column("id", "ID", width=80, align="right"),
    Column("project", width=170),
    Column("status", width=110, filterable=True,
           renderer=badge_renderer({"Active": "success", "Paused": "warning", "Failed": "error"})),
    Column("owner", width=110, filterable=True),
    Column("progress", width=170, renderer=progress_renderer()),
    Column("cost", align="right", formatter=lambda v: f"${v:,.2f}"),
], rows, page_size=8, selection="multi")
demo.setMinimumHeight(430)
```

## Usage guidance

- Right-align numbers so that magnitudes line up.
- Use page_size=None only with a small row count, or keep a filter visible.

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
