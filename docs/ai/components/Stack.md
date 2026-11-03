# Stack

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Arranges children in a row or column with token spacing.

Group: Layout. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Stack
```

## Signature

```python
Stack(children=None, parent=None, direction='vertical', spacing=2, padding=0, align='stretch')
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `children` | `None` | Initial widgets. |
| `parent` | `None` | Parent widget. |
| `direction` | `'vertical'` | vertical or horizontal. |
| `spacing` | `2` | Spacing token step (2 means 8 px). |
| `padding` | `0` | Spacing token step around the content. |
| `align` | `'stretch'` | start, center, end or stretch on the cross axis. |

## Public methods

- `add(widget, stretch: int = 0)`: Add a widget and return it.
- `add_spacing(step: int)`: Add fixed space by token step.
- `add_stretch(stretch: int = 1)`: Add flexible empty space.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Badge, Button, Stack

row = Stack([Button("One"), Button("Two"), Button("Three")], direction="horizontal", spacing=2)
demo = Stack([row, Badge("Vertical stack, spacing token 3", variant="primary")], spacing=3, align="start")
```

## Usage guidance

- Spacing takes token steps, which keeps the 4 px rhythm without magic numbers.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
