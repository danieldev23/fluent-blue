# RangeSlider

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A slider with two handles that selects a range.

Group: Selection. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import RangeSlider
```

## Signature

```python
RangeSlider(low=20, high=80, parent=None, minimum=0, maximum=100, step=1, disabled=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `low` | `20` | Initial lower value. |
| `high` | `80` | Initial upper value. |
| `parent` | `None` | Parent widget. |
| `minimum` | `0` | Lowest allowed value. |
| `maximum` | `100` | Highest allowed value. |
| `step` | `1` | Granularity of values. |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- `range_changed(int, int)`: The new lower and upper values.

## Public methods

- `high() -> int`
- `low() -> int`
- `set_range(low: int, high: int)`: Set both values, clamped, snapped and ordered. Emits range_changed if either changed.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import RangeSlider, Stack, Text

readout = Text("Price: $200 to $800", color="text-secondary")
slider = RangeSlider(200, 800, minimum=0, maximum=1000, step=50)
slider.range_changed.connect(lambda low, high: readout.setText(f"Price: ${low} to ${high}"))
demo = Stack([slider, readout], spacing=2)
```

## Usage guidance

- Show the chosen range in text next to the slider.
- Use step to avoid meaningless precision.
- Up and Down choose the handle, Left and Right move it.

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
