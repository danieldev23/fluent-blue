# Tag

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A compact label for categories, optionally closable.

Group: Data Display. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Tag
```

## Signature

```python
Tag(text='', parent=None, variant='neutral', closable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `text` | `''` | Content. |
| `parent` | `None` | Parent widget. |
| `variant` | `'neutral'` | Same options as Badge. |
| `closable` | `False` | Show a close button. |

## Signals

- `closed(str)`: The close button was used; carries the text. The tag hides itself.

## Public methods

- `text() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Stack, Tag

demo = Stack([Tag("Design"), Tag("Python", variant="primary"), Tag("Stable", variant="success"),
              Tag("Beta", variant="warning"), Tag("Removable", closable=True)], direction="horizontal", align="center")
```

## Usage guidance

- Use tags for categories that people add or remove; use badges for status.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
