# Drawer

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A panel that slides in from the edge of a window.

Group: Layout. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Drawer
```

## Signature

```python
Drawer(parent, title='', placement='right', width=360, dismissible=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `required` | Any widget in the target window. |
| `title` | `''` | Header title. |
| `placement` | `'right'` | left or right. |
| `width` | `360` | Panel width in pixels. |
| `dismissible` | `True` | Close on Escape and on clicks on the scrim. |

## Signals

- `opened()`: The drawer started opening.
- `closed()`: The drawer finished closing.

## Public methods

- `add(widget, stretch: int = 0)`: Add a widget to the body and return it.
- `close_drawer()`: Slide the drawer out.
- `is_open() -> bool`
- `open_drawer()`: Slide the drawer in and move focus to it.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Drawer, FormField, Input, Stack

demo = Stack([Button("Open drawer", icon="sidebar", variant="primary")], align="start")
trigger = demo.findChildren(Button)[0]

def open_drawer():
    drawer = Drawer(demo, title="Edit profile")
    drawer.add(FormField("Name", Input("Ada Lovelace")))
    drawer.add(Button("Save", variant="primary"))
    drawer.body.addStretch(1)
    drawer.closed.connect(drawer.deleteLater)
    drawer.open_drawer()

trigger.clicked.connect(open_drawer)
```

## Usage guidance

- Use when people need to keep the page in view while they work.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
