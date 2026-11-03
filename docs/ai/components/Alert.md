# Alert

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

An inline message in the page flow.

Group: Feedback. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Alert
```

## Signature

```python
Alert(title='', message='', parent=None, variant='info', closable=False, action_text='', dense=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `title` | `''` | Bold first line. |
| `message` | `''` | Body text. |
| `parent` | `None` | Parent widget. |
| `variant` | `'info'` | info, success, warning or error. |
| `closable` | `False` | Show a dismiss button. |
| `action_text` | `''` | Label of an optional action. |
| `dense` | `False` | Use tighter spacing and smaller text. |

## Signals

- `closed()`: The alert was dismissed.
- `action_clicked()`: The action was used.

## Public methods

- `dismiss()`: Hide the alert and emit closed.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Alert, Stack

demo = Stack([
    Alert("Heads up", "A new version is available.", variant="info", action_text="Update"),
    Alert("Saved", "All changes are stored.", variant="success", closable=True),
    Alert("Storage almost full", "You have used 92% of your quota.", variant="warning"),
    Alert("Connection lost", "We will retry in 30 seconds.", variant="error", closable=True),
])
```

## Usage guidance

- Use for persistent, in-context messages. Use Toast for passing confirmation.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
