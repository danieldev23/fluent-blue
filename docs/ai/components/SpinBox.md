# SpinBox

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

An integer input with stepper buttons.

Group: Selection. Qt base: `QSpinBox`, whose full API stays available.

## Import

```python
from fluent_blue import SpinBox
```

## Signature

```python
SpinBox(value=0, parent=None, minimum=0, maximum=100, step=1, suffix='', disabled=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `value` | `0` | Initial value. |
| `parent` | `None` | Parent widget. |
| `minimum` | `0` | Lower bound. |
| `maximum` | `100` | Upper bound. |
| `step` | `1` | Step amount. |
| `suffix` | `''` | Text after the value, such as " px". |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- Inherits valueChanged(int) from QSpinBox.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import SpinBox

demo = SpinBox(16, minimum=8, maximum=72, suffix=" px")
```

## Usage guidance

- Add a suffix so that the unit is never ambiguous.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
