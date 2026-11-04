# Rating

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A star rating that can be set with the mouse or the keyboard.

Group: Selection. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Rating
```

## Signature

```python
Rating(value=0, parent=None, count=5, allow_half=False, allow_clear=True, read_only=False, size=22, disabled=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `value` | `0` | Initial value from 0 to count. |
| `parent` | `None` | Parent widget. |
| `count` | `5` | Number of stars. |
| `allow_half` | `False` | Allow half-star values. |
| `allow_clear` | `True` | Clicking the current value again resets it to 0. |
| `read_only` | `False` | Display only; the value cannot be changed by the user. |
| `size` | `22` | Star size in pixels. |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- `value_changed(float)`: The new value, after a change by the user or by set_value.

## Public methods

- `count() -> int`
- `set_value(value: float)`: Set the value, clamped and snapped to the step. Emits value_changed if it changed.
- `step() -> float`
- `value() -> float`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Rating, Stack, Text, Toast

live = Rating(3)
caption = Text("3 of 5", color="text-secondary")
live.value_changed.connect(lambda value: caption.setText(f"{value:g} of 5"))
demo = Stack([
    Stack([live, caption], direction="horizontal", align="center", spacing=3),
    Rating(3.5, allow_half=True, size=26),
    Rating(4, read_only=True, size=18),
], spacing=3)
```

## Usage guidance

- Use half stars only when the average is shown with that precision.
- Clicking the current value again clears it; pass allow_clear=False to prevent that.
- Set read_only=True to display an average rating.

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
