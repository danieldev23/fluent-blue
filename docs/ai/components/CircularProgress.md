# CircularProgress

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A circular progress indicator, which also serves as a spinner.

Group: Data Display. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import CircularProgress
```

## Signature

```python
CircularProgress(value=0, parent=None, minimum=0, maximum=100, indeterminate=False, variant='primary', size=48, thickness=4, show_label=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `value` | `0` | Current value. |
| `parent` | `None` | Parent widget. |
| `minimum` | `0` | Lower bound. |
| `maximum` | `100` | Upper bound. |
| `indeterminate` | `False` | Spin without a known value. |
| `variant` | `'primary'` | primary, success, warning, error or info. |
| `size` | `48` | Outer diameter in pixels. |
| `thickness` | `4` | Stroke width in pixels. |
| `show_label` | `True` | Show the percentage at the center. |

## Signals

- `value_changed(float)`: The value changed.

## Public methods

- `fraction() -> float`
- `is_indeterminate() -> bool`
- `set_indeterminate(on: bool)`
- `set_value(value: float)`: Set the value, clamped to the bounds.
- `value() -> float`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import CircularProgress, Stack

demo = Stack([CircularProgress(25), CircularProgress(72, variant="success"), CircularProgress(90, variant="warning", size=64),
              CircularProgress(indeterminate=True, size=32, thickness=3)], direction="horizontal", align="center", spacing=4)
```

## Usage guidance

- Use in compact spaces, or as a spinner with indeterminate=True.

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
