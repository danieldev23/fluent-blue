# ConfirmDialog

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Ask the user to confirm an action.

Group: Feedback. Qt base: `QDialog`, whose full API stays available.

## Import

```python
from fluent_blue import ConfirmDialog
```

## Signature

```python
ConfirmDialog(parent=None, title='Are you sure?', message='', confirm_text='Confirm', cancel_text='Cancel', danger=False, variant='info', buttons=('OK',), content=None, width=460, closable=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Owner window. |
| `title` | `'Are you sure?'` | Header title. |
| `message` | `''` | Body text; state the consequence. |
| `confirm_text` | `'Confirm'` | Label of the confirm button; use a verb. |
| `cancel_text` | `'Cancel'` | Label of the cancel button. |
| `danger` | `False` | Style the confirm button as destructive. |
| `variant` | `'info'` | info, success, warning or error. |
| `buttons` | `('OK',)` | Labels from left to right; the last one is primary. |
| `content` | `None` | Text or a widget for the body. |
| `width` | `460` | Panel width in pixels. |
| `closable` | `True` | Allow closing with the header button and Escape. |

## Signals

- `confirmed()`: The action was confirmed.
- `cancelled()`: The dialog closed in any other way.
- `button_clicked(str)`: The label of the chosen button.
- `closed()`: The dialog was hidden, regardless of outcome. Inherits accepted and rejected from QDialog.

## Public methods

- `add_action(button)`: Add a button to the footer and return it.
- `ask(cls, parent, title: str, message: str = , *, confirm_text: str = Confirm, danger: bool = False) -> bool`: Block until answered. Returns True if confirmed.
- `button(label: str) -> Button`
- `reject()`
- `show_message(cls, parent, title: str, message: str, variant: str = info) -> str | None`: Block until the dialog closes and return the chosen label.
- `was_confirmed() -> bool`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import ConfirmDialog, DangerButton, Toast

demo = DangerButton("Delete project", icon="trash")

def ask():
    dialog = ConfirmDialog(demo, title="Delete this project?", message="All its data is removed. This cannot be undone.",
                           confirm_text="Delete project", danger=True)
    dialog.confirmed.connect(lambda: Toast.show("Project deleted", parent=demo, variant="success"))
    dialog.finished.connect(dialog.deleteLater)
    dialog.open()

demo.clicked.connect(ask)
```

## Usage guidance

- State the consequence, and label the button with the action, not “OK”.

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
