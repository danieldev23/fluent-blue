# Notification

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A richer message with a title and an action, which stays until dismissed by default.

Group: Feedback. Plain Python helper.

## Import

```python
from fluent_blue import Notification
```

## Signature

```python
Notification.show(title, message='', parent=None, variant='info', duration=0, action_text='', on_action=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `title` | `required` | Headline. |
| `message` | `''` | Body text. |
| `parent` | `None` | Any widget of the target window; defaults to the active window. |
| `variant` | `'info'` | info, success, warning or error. |
| `duration` | `0` | Milliseconds before dismissal; 0 keeps it until dismissed. |
| `action_text` | `''` | Action label. |
| `on_action` | `None` | Callable to run when the action is used. |

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Notification

demo = Button("Notify", icon="bell", variant="primary")
demo.clicked.connect(lambda: Notification.show("Export finished", "Your report is ready to download.", parent=demo,
                                               variant="success", action_text="Open"))
```

## Usage guidance

- Use for events that deserve attention until acknowledged.

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
