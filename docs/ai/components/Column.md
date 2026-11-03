# Column

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Describes one table column.

Group: Data Tables. Plain Python helper.

## Import

```python
from fluent_blue import Column
```

## Signature

```python
Column(key, title='', width=None, sortable=True, filterable=False, visible=True, align='left', formatter=None, renderer=None, sort_key=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `key` | `required` | Key of the value in each row dict. |
| `title` | `''` | Header text; defaults to the key in title case. |
| `width` | `None` | Initial width in pixels; None leaves it to the table. |
| `sortable` | `True` | Allow sorting by this column. |
| `filterable` | `False` | Offer this column's values in the filter menu. |
| `visible` | `True` | Initially visible. |
| `align` | `'left'` | left, center or right. |
| `formatter` | `None` | callable(value) -> str for the display text. |
| `renderer` | `None` | callable(painter, rect, value, row) for custom painting. |
| `sort_key` | `None` | callable(value) to override the sort value. |

## Public methods

- `text(value: Any) -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Column, DataTable

demo = DataTable([
    Column("name", "Full name", width=200),
    Column("salary", align="right", formatter=lambda v: f"${v:,}"),
    Column("note", sortable=False, visible=False),
], [{"name": "Ada", "salary": 120000, "note": "hidden"}, {"name": "Grace", "salary": 134000, "note": "hidden"}],
    page_size=None, exportable=False)
demo.setMinimumHeight(190)
```

## Usage guidance

- Formatters change only the display, so sorting still uses the raw value.

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
