# TreeView

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A tree from nested dicts, with built-in filtering.

Group: Advanced Components. Qt base: `QTreeView`, whose full API stays available.

## Import

```python
from fluent_blue import TreeView
```

## Signature

```python
TreeView(items=None, parent=None, expand_all=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `items` | `None` | Dicts with text and optional id, icon and children. |
| `parent` | `None` | Parent widget. |
| `expand_all` | `True` | Expand every node initially. |

## Signals

- `item_selected(object)`: The id of the current item.
- `item_activated(object)`: The id of an item activated by double-click or Enter.

## Public methods

- `current_id()`
- `set_filter(text: str)`: Show only matching items and their ancestors.
- `set_items(items)`: Replace the tree.
- `visible_count() -> int`: Visible items, counting expanded and collapsed descendants.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import TreeView

demo = TreeView([
    {"text": "Design system", "icon": "layers", "children": [
        {"text": "Foundations", "icon": "ruler", "children": [{"text": "Colors", "icon": "palette"}, {"text": "Type", "icon": "type"}]},
        {"text": "Components", "icon": "box"},
    ]},
    {"text": "Releases", "icon": "tag"},
])
demo.setMinimumHeight(190)
```

## Usage guidance

- set_filter keeps matching items along with their ancestors, so context is kept.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
