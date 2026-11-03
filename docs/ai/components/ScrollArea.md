# ScrollArea

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A frameless scroll area with themed scrollbars and a resizable content widget.

Group: Layout. Qt base: `QScrollArea`, whose full API stays available.

## Import

```python
from fluent_blue import ScrollArea
```

## Signature

```python
ScrollArea(widget=None, parent=None, horizontal=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `widget` | `None` | Content widget. |
| `parent` | `None` | Parent widget. |
| `horizontal` | `False` | Allow horizontal scrolling. |

## Public methods

- `scroll_to_top()`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import ListItem, ScrollArea, Stack

demo = ScrollArea(Stack([ListItem(f"Row {n}", icon="file") for n in range(1, 21)], spacing=1))
demo.setFixedHeight(150)
```

## Usage guidance

- Avoid nested vertical scrolling; it traps the mouse wheel.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
