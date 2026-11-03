# ProgressDialog

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A modal that reports the progress of a long operation.

Group: Feedback. Qt base: `QDialog`, whose full API stays available.

## Import

```python
from fluent_blue import ProgressDialog
```

## Signature

```python
ProgressDialog(parent=None, title='Working…', message='', maximum=100, cancellable=True, auto_close=True, content=None, width=460, closable=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Owner window. |
| `title` | `'Working…'` | Header title. |
| `message` | `''` | Status text. |
| `maximum` | `100` | Value at completion. |
| `cancellable` | `True` | Show a cancel button. |
| `auto_close` | `True` | Close automatically at completion. |
| `content` | `None` | Text or a widget for the body. |
| `width` | `460` | Panel width in pixels. |
| `closable` | `True` | Allow closing with the header button and Escape. |

## Signals

- `canceled()`: The user asked to cancel.
- `closed()`: The dialog was hidden, regardless of outcome. Inherits accepted and rejected from QDialog.

## Public methods

- `add_action(button)`: Add a button to the footer and return it.
- `cancel()`: Flag cancellation, emit canceled and close.
- `reject()`
- `set_message(message: str)`
- `set_value(value: float)`: Update progress; at the maximum the dialog closes if auto_close is set.
- `value() -> float`
- `was_canceled() -> bool`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, ProgressDialog
from fluent_blue.compatibility.qt import QTimer

demo = Button("Start export", icon="download", variant="primary")

def run():
    dialog = ProgressDialog(demo, title="Exporting", message="Writing 1,204 rows…")
    timer = QTimer(dialog)
    timer.setInterval(40)
    timer.timeout.connect(lambda: dialog.set_value(dialog.value() + 1))
    dialog.finished.connect(lambda _r: timer.stop())
    timer.start()
    dialog.open()

demo.clicked.connect(run)
```

## Usage guidance

- Offer Cancel whenever the work can stop safely.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
