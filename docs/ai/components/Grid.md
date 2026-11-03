# Grid

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A grid with a fixed column count, or responsive columns from a minimum width.

Group: Layout. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Grid
```

## Signature

```python
Grid(parent=None, columns=3, min_column_width=None, gap=3)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `columns` | `3` | Fixed column count. Ignored if min_column_width is set. |
| `min_column_width` | `None` | Reflow to fit as many columns of this width as possible. |
| `gap` | `3` | Spacing token step between cells. |

## Public methods

- `add(widget, col_span: int = 1)`: Add a widget spanning col_span columns and return it.
- `column_count() -> int`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Card, Grid

demo = Grid(min_column_width=180)
for number in range(1, 7):
    demo.add(Card(title=f"Cell {number}", subtitle="Reflows with width."))
```

## Usage guidance

- Set min_column_width for responsive layouts, or columns for a fixed one.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
