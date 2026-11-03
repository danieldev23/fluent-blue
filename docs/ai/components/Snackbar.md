# Snackbar

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A single-line message at the bottom center, often offering an undo.

Group: Feedback. Plain Python helper.

## Import

```python
from fluent_blue import Snackbar
```

## Signature

```python
Snackbar.show(message, parent=None, action_text='', on_action=None, duration=4000)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `message` | `required` | Text. |
| `parent` | `None` | Any widget of the target window; defaults to the active window. |
| `action_text` | `''` | Action label, such as "Undo". |
| `on_action` | `None` | Callable to run when the action is used. |
| `duration` | `4000` | Milliseconds before dismissal. |

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Snackbar

demo = Button("Archive item", icon="archive")
demo.clicked.connect(lambda: Snackbar.show("Item archived", parent=demo, action_text="Undo"))
```

## Usage guidance

- Prefer an undo over a confirmation dialog for reversible actions.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
