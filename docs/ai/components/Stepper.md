# Stepper

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Shows progress through ordered steps. Arrow keys move when clickable.

Group: Advanced Components. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Stepper
```

## Signature

```python
Stepper(steps=None, parent=None, current=0, clickable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `steps` | `None` | Step titles. |
| `parent` | `None` | Parent widget. |
| `current` | `0` | Current 0-based step. |
| `clickable` | `False` | Allow moving to completed steps by mouse and keyboard. |

## Signals

- `current_changed(int)`: The current step changed.
- `step_clicked(int)`: A step was chosen by the user.

## Public methods

- `current() -> int`
- `set_current(index: int)`: Move to a step, clamped to the range.
- `set_error(index: int, error: bool = True)`: Mark a step as failed.
- `steps() -> list[str]`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Stepper

demo = Stepper(["Account", "Workspace", "Billing", "Done"], current=2, clickable=True)
```

## Usage guidance

- Keep to three to six steps with short titles.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
