# Pagination

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Page navigation with ellipsis and optional range text.

Group: Navigation. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Pagination
```

## Signature

```python
Pagination(parent=None, total=0, page_size=10, page=1, siblings=1, show_total=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `total` | `0` | Number of items. |
| `page_size` | `10` | Items per page. |
| `page` | `1` | Current 1-based page. |
| `siblings` | `1` | Pages shown on each side of the current one. |
| `show_total` | `True` | Show "1-10 of 200". |

## Signals

- `page_changed(int)`: The new 1-based page.

## Public methods

- `page() -> int`
- `page_count() -> int`
- `set_page(page: int)`: Go to a page, clamped to the valid range.
- `set_page_size(size: int)`
- `set_total(total: int)`
- `visible_pages() -> list[int | None]`: Page numbers to display; None marks an ellipsis.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Pagination

demo = Pagination(total=1280, page_size=20, page=7)
```

## Usage guidance

- Show the range so people know how much data exists.

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
