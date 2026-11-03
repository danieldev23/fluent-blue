# ColorPicker

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A swatch button that opens a saturation/value square, hue bar, hex field and presets.

Group: Advanced Components. Qt base: `QPushButton`, whose full API stays available.

## Import

```python
from fluent_blue import ColorPicker
```

## Signature

```python
ColorPicker(parent=None, color='#1677FF', presets=('primary-500', 'primary-300', 'primary-800', 'success', 'warning', 'error', 'info', 'gray-500', 'gray-900'), text='', variant=None, size='medium', icon=None, icon_position='left', loading=False, disabled=False, full_width=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `color` | `'#1677FF'` | Initial color as #RRGGBB. |
| `presets` | `('primary-500', 'primary-300', 'primary-800', 'success', 'warning', 'error', 'info', 'gray-500', 'gray-900')` | Hex values or color roles offered as shortcuts. |
| `text` | `''` | Button label. |
| `variant` | `None` | primary, secondary, outline, ghost, text or danger. |
| `size` | `'medium'` | small, medium or large. |
| `icon` | `None` | Icon name or QIcon. |
| `icon_position` | `'left'` | left or right. |
| `loading` | `False` | Show a spinner and ignore clicks. |
| `disabled` | `False` | Start disabled. |
| `full_width` | `False` | Expand to fill the available width. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- `color_changed(str)`: The new color as uppercase #RRGGBB.

## Public methods

- `color() -> str`
- `is_loading() -> bool`
- `open_popup()`: Open the picker popup.
- `set_color(color: str)`: Set the color and emit color_changed if it changed.
- `set_full_width(full: bool)`
- `set_icon(icon: str | QIcon | None)`: Set the icon by name or QIcon; None removes it.
- `set_icon_position(position: str)`
- `set_loading(loading: bool)`: Show or hide the spinner. While loading, the button ignores clicks and keys.
- `set_size(size: str)`
- `set_variant(variant: str)`
- `size_name() -> str`
- `variant() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import ColorPicker

demo = ColorPicker(color="#1677FF")
```

## Usage guidance

- Presets accept color roles, so they follow the active theme.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
