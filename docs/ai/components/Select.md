# Select

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Choose one value from a list.

Group: Selection. Qt base: `QComboBox`, whose full API stays available.

## Import

```python
from fluent_blue import Select
```

## Signature

```python
Select(options=None, parent=None, value=None, placeholder='', size='medium', disabled=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `options` | `None` | "a", ("Label", value) or {"label": ..., "value": ...} entries. |
| `parent` | `None` | Parent widget. |
| `value` | `None` | Initial value. |
| `placeholder` | `''` | Text shown while nothing is selected. |
| `size` | `'medium'` | small, medium or large. |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- `value_changed(object)`: The newly selected value.

## Public methods

- `set_options(options)`: Replace the options without emitting value_changed.
- `set_value(value)`: Select by value. Raises ValueError if the value is not an option.
- `value()`: The selected value, or None.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Select, Stack

demo = Stack([
    Select(["Design", "Engineering", "Marketing"], placeholder="Choose a team"),
    Select([("Weekly", 7), ("Monthly", 30)], value=30),
    Select(["Disabled"], disabled=True),
], direction="horizontal")
```

## Usage guidance

- Prefer it over radio buttons when there are more than five options.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
