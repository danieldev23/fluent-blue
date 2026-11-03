# FluentWindow

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A frameless base window styled with Fluent Blue design language.

Group: Layout. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import FluentWindow
```

## Signature

```python
FluentWindow(parent=None, title='Fluent Blue Application', icon_name=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `title` | `'Fluent Blue Application'` | Window title. |
| `icon_name` | `None` | Optional icon name from Fluent Blue icon system. |

## Public methods

- `set_central_widget(widget: QWidget)`: Set the main content area widget.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, FluentWindow

launch = Button("Open window", icon="external-link", variant="primary")
window = FluentWindow(title="Fluent Blue Application")
window.set_central_widget(Button("Central content"))
window.resize(480, 280)
launch.clicked.connect(window.show)
demo = launch
```

## Usage guidance

- Keep the keyboard shortcuts for closing the window working when you customize it.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
