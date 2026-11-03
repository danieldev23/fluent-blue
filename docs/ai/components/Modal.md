# Modal

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A themed modal dialog over a dimmed parent window.

Group: Layout. Qt base: `QDialog`, whose full API stays available.

## Import

```python
from fluent_blue import Modal
```

## Signature

```python
Modal(parent=None, title='', content=None, width=460, closable=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Owner window. |
| `title` | `''` | Header title. |
| `content` | `None` | Text or a widget for the body. |
| `width` | `460` | Panel width in pixels. |
| `closable` | `True` | Allow closing with the header button and Escape. |

## Signals

- `closed()`: The dialog was hidden, regardless of outcome. Inherits accepted and rejected from QDialog.
- Inherits accepted and rejected from QDialog.

## Public methods

- `add_action(button)`: Add a button to the footer and return it.
- `reject()`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, FormField, Input, Modal

demo = Button("Open modal", variant="primary")

def show():
    modal = Modal(demo, title="Rename project")
    modal.body.addWidget(FormField("Name", Input("Fluent Blue")))
    modal.add_action(Button("Cancel")).clicked.connect(modal.reject)
    modal.add_action(Button("Rename", variant="primary")).clicked.connect(modal.accept)
    modal.open()

demo.clicked.connect(show)
```

## Usage guidance

- Modals stop everything, so keep them short and focused on one decision.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
