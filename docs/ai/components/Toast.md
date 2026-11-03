# Toast

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A brief, auto-dismissing message in the window's top right corner.

Group: Feedback. Plain Python helper.

## Import

```python
from fluent_blue import Toast
```

## Signature

```python
Toast.show(message, parent=None, variant='info', duration=3500)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `message` | `required` | Text. |
| `parent` | `None` | Any widget of the target window; defaults to the active window. |
| `variant` | `'info'` | info, success, warning or error. |
| `duration` | `3500` | Milliseconds before dismissal, paused on hover. 0 keeps it open. |

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Stack, Toast

def button(text, variant):
    b = Button(text)
    b.clicked.connect(lambda: Toast.show(f"{text} toast message", parent=b, variant=variant))
    return b

demo = Stack([button("Info", "info"), button("Success", "success"), button("Warning", "warning"), button("Error", "error")],
             direction="horizontal")
```

## Usage guidance

- Keep it to one sentence. People may not see it before it goes.
- Do not put errors requiring action here; use Alert or a dialog.

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
