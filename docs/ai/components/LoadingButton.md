# LoadingButton

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A primary button with start() and stop() shortcuts for async work.

Group: Buttons. Qt base: `QPushButton`, whose full API stays available.

## Import

```python
from fluent_blue import LoadingButton
```

## Signature

```python
LoadingButton(text='', parent=None, loading_text=None, variant=None, size='medium', icon=None, icon_position='left', loading=False, disabled=False, full_width=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `text` | `''` | Button label. |
| `parent` | `None` | Parent widget. |
| `loading_text` | `None` | Label to show while loading; the original label returns on stop(). |
| `variant` | `None` | primary, secondary, outline, ghost, text or danger. |
| `size` | `'medium'` | small, medium or large. |
| `icon` | `None` | Icon name or QIcon. |
| `icon_position` | `'left'` | left or right. |
| `loading` | `False` | Show a spinner and ignore clicks. |
| `disabled` | `False` | Start disabled. |
| `full_width` | `False` | Expand to fill the available width. |
| `tooltip` | `None` | Tooltip text. |

## Public methods

- `is_loading() -> bool`
- `set_full_width(full: bool)`
- `set_icon(icon: str | QIcon | None)`: Set the icon by name or QIcon; None removes it.
- `set_icon_position(position: str)`
- `set_loading(loading: bool)`: Show or hide the spinner. While loading, the button ignores clicks and keys.
- `set_size(size: str)`
- `set_variant(variant: str)`
- `size_name() -> str`
- `start()`: Enter the loading state.
- `stop()`: Leave the loading state and restore the label.
- `variant() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import LoadingButton
from fluent_blue.compatibility.qt import QTimer

demo = LoadingButton("Save changes", loading_text="Saving…")

def save():
    demo.start()
    QTimer.singleShot(1500, demo.stop)

demo.clicked.connect(save)
```

## Usage guidance

- Keep the button's width stable by using a similar loading label.
- Clicks are ignored while loading, so double submission cannot happen.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
