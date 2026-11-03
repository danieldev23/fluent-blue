# Panel

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A titled section with a header action area.

Group: Layout. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Panel
```

## Signature

```python
Panel(title='', parent=None, actions=None, padding=4)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `title` | `''` | Header title. |
| `parent` | `None` | Parent widget. |
| `actions` | `None` | Widgets placed at the right of the header. |
| `padding` | `4` | Spacing token step around the body. |

## Public methods

- `add(widget, stretch: int = 0)`: Add a widget to the body and return it.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import IconButton, Panel, Text

demo = Panel("Details", actions=[IconButton("refresh", size="small", tooltip="Refresh"), IconButton("more-horizontal", size="small", tooltip="More")])
demo.add(Text("Panels have a header with an action area.", color="text-secondary"))
```

## Usage guidance

- Use for tool regions in app layouts. Use Card for self-contained content.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
