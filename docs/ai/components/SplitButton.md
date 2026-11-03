# SplitButton

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Primary action on the left, a menu of related actions on the right.

Group: Buttons. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import SplitButton
```

## Signature

```python
SplitButton(text='', parent=None, items=None, variant='primary', size='medium', icon=None, disabled=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `text` | `''` | Label of the main action. |
| `parent` | `None` | Parent widget. |
| `items` | `None` | Menu entries, accepted in every form Menu understands. |
| `variant` | `'primary'` | Button variant applied to both parts. |
| `size` | `'medium'` | small, medium or large. |
| `icon` | `None` | Icon of the main action. |
| `disabled` | `False` | Start disabled. |

## Signals

- `clicked()`: The main action was activated.
- `item_triggered(str)`: A menu entry was chosen; carries its id.

## Public methods

- `show_menu()`: Open the menu below the control.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import SplitButton

demo = SplitButton("Save", icon="save", items=[
    {"text": "Save as…", "icon": "file"},
    {"text": "Save a copy", "icon": "copy"},
    None,
    {"text": "Discard", "icon": "trash", "danger": True},
])
```

## Usage guidance

- The main action should be what most people want most of the time.
- Menu entries should be variations of the same task.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
