# FileTree

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A lazily loaded file system tree, using QFileSystemModel.

Group: Advanced Components. Qt base: `QTreeView`, whose full API stays available.

## Import

```python
from fluent_blue import FileTree
```

## Signature

```python
FileTree(root='', parent=None, name_filters=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `root` | `''` | Root directory. |
| `parent` | `None` | Parent widget. |
| `name_filters` | `None` | Patterns such as ["*.py"]; others are hidden. |

## Signals

- `file_selected(str)`: The path of the current item.
- `file_activated(str)`: The path of a file activated by double-click or Enter.

## Public methods

- `current_path() -> str`
- `root() -> str`
- `set_root(path: str)`: Show a directory as the root.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from pathlib import Path

import fluent_blue
from fluent_blue import FileTree

demo = FileTree(str(Path(fluent_blue.__file__).parent), name_filters=["*.py"])
demo.setMinimumHeight(190)
```

## Usage guidance

- Directories load lazily, so large folders stay fast.

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
