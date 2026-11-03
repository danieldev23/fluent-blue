# Avatar

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A user image or initials.

Group: Data Display. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Avatar
```

## Signature

```python
Avatar(name='', parent=None, image=None, size='medium', shape='circle', status=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `name` | `''` | Used for initials, the fallback color and the accessible name. |
| `parent` | `None` | Parent widget. |
| `image` | `None` | Image path or QPixmap. |
| `size` | `'medium'` | small, medium, large, xl or a pixel size. |
| `shape` | `'circle'` | circle or square. |
| `status` | `None` | Optional presence dot: online, away, busy or offline. |

## Public methods

- `initials() -> str`
- `set_image(image)`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Avatar, Stack

demo = Stack([Avatar("Ada Lovelace", size="small"), Avatar("Grace Hopper", status="online"),
              Avatar("Alan Turing", size="large", status="busy"), Avatar("Linus Pauling", size="xl", status="away"),
              Avatar("Team Rocket", size="large", shape="square")], direction="horizontal", align="center")
```

## Usage guidance

- Colors are derived from the name, so one person always looks the same.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
