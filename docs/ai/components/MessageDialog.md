# MessageDialog

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A modal with a status icon, a message and buttons.

Group: Feedback. Qt base: `QDialog`, whose full API stays available.

## Import

```python
from fluent_blue import MessageDialog
```

## Signature

```python
MessageDialog(parent=None, title='', message='', variant='info', buttons=('OK',), content=None, width=460, closable=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Owner window. |
| `title` | `''` | Header title. |
| `message` | `''` | Body text. |
| `variant` | `'info'` | info, success, warning or error. |
| `buttons` | `('OK',)` | Labels from left to right; the last one is primary. |
| `content` | `None` | Text or a widget for the body. |
| `width` | `460` | Panel width in pixels. |
| `closable` | `True` | Allow closing with the header button and Escape. |

## Signals

- `button_clicked(str)`: The label of the chosen button.
- `closed()`: The dialog was hidden, regardless of outcome. Inherits accepted and rejected from QDialog.

## Public methods

- `add_action(button)`: Add a button to the footer and return it.
- `button(label: str) -> Button`
- `reject()`
- `show_message(cls, parent, title: str, message: str, variant: str = info) -> str | None`: Block until the dialog closes and return the chosen label.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, MessageDialog

demo = Button("Show message")

def show():
    dialog = MessageDialog(demo, title="Update installed", message="Restart the app to finish.", variant="success",
                           buttons=("Later", "Restart"))
    dialog.finished.connect(dialog.deleteLater)
    dialog.open()

demo.clicked.connect(show)
```

## Usage guidance

- Interrupt only for information people must see now.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Never connect a lambda or closure that captures a widget to `ThemeManager` signals: it outlives the widget, and PyQt aborts when it fires. Use `ThemedMixin` or a bound method.
- Keep theme switches fast: do not rebuild child widgets in `refresh_theme()`, and free one-shot menus and dialogs with `WA_DeleteOnClose` or `finished.connect(dialog.deleteLater)`.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
