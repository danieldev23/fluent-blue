# MultiSelect

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Choose any number of values from a checkable popup list.

Group: Selection. Qt base: `QPushButton`, whose full API stays available.

## Import

```python
from fluent_blue import MultiSelect
```

## Signature

```python
MultiSelect(options=None, parent=None, values=None, placeholder='Select…', max_labels=2, disabled=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `options` | `None` | Entries, in the same forms as Select. |
| `parent` | `None` | Parent widget. |
| `values` | `None` | Initially selected values. |
| `placeholder` | `'Select…'` | Text shown while nothing is selected. |
| `max_labels` | `2` | Labels listed before the text collapses to a count. |
| `disabled` | `False` | Start disabled. |

## Signals

- `values_changed(list)`: The selected values, in option order.

## Public methods

- `set_options(options)`
- `set_values(values)`: Replace the selection and emit values_changed if it changed.
- `show_popup()`: Open the checkable list under the control.
- `values() -> list`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import MultiSelect

demo = MultiSelect(["Python", "Rust", "Go", "TypeScript"], values=["Python", "Rust"], placeholder="Languages")
```

## Usage guidance

- The label collapses to a count, so the control keeps its width.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
