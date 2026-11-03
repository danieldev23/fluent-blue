# Text

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A label bound to a typography role and a text color role.

Group: Data Display. Qt base: `QLabel`, whose full API stays available.

## Import

```python
from fluent_blue import Text
```

## Signature

```python
Text(text='', parent=None, style='body-medium', color='text-primary', wrap=False, selectable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `text` | `''` | Content. |
| `parent` | `None` | Parent widget. |
| `style` | `'body-medium'` | Typography role such as heading-2 or body-medium. |
| `color` | `'text-primary'` | Text color role such as text-secondary. |
| `wrap` | `False` | Enable word wrap. |
| `selectable` | `False` | Allow mouse selection. |

## Public methods

- `set_color(color: str)`
- `set_style(style: str)`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Stack, Text

demo = Stack([
    Text("Display heading", style="heading-1"),
    Text("Body text in a secondary color.", color="text-secondary"),
    Text("Caption with tertiary color", style="caption", color="text-tertiary"),
    Text("print('monospace')", style="monospace", color="primary-text"),
], spacing=1)
```

## Usage guidance

- Use typography roles, never ad hoc sizes, so that hierarchy stays consistent.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
