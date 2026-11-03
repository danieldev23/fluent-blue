# Menu

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A popup menu.

Group: Navigation. Qt base: `QMenu`, whose full API stays available.

## Import

```python
from fluent_blue import Menu
```

## Signature

```python
Menu(parent=None, items=None, title='')
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `items` | `None` | A list of str, MenuItem, dict (MenuItem keyword arguments plus text, optional items for a submenu) or None for a separator. |
| `title` | `''` | Title when used as a submenu. |

## Signals

- `item_triggered(str)`: The id of the chosen entry.

## Public methods

- `add_item(item)`: Add one entry in any accepted form and return the created action or submenu.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Menu

demo = Button("Open menu", icon="menu")
menu = Menu(demo, items=[
    {"text": "New file", "icon": "file", "shortcut": "Ctrl+N"},
    {"text": "Open…", "icon": "folder-open", "shortcut": "Ctrl+O"},
    None,
    {"text": "Export", "items": ["PDF", "CSV", "JSON"]},
    {"text": "Show hidden files", "checkable": True, "checked": True},
    None,
    {"text": "Delete", "icon": "trash", "danger": True},
])
demo.clicked.connect(lambda: menu.popup(demo.mapToGlobal(demo.rect().bottomLeft())))
```

## Usage guidance

- Keep menus short and put destructive entries last, after a separator.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
