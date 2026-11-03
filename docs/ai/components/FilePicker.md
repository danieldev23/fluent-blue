# FilePicker

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A path field with a browse button and drag and drop.

Group: Advanced Components. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import FilePicker
```

## Signature

```python
FilePicker(parent=None, mode='open', filter='', placeholder='No file selected', button_text='Browse…', disabled=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `mode` | `'open'` | open, open-multiple, save or directory. |
| `filter` | `''` | Qt name filter, such as "Images (*.png *.jpg)". |
| `placeholder` | `'No file selected'` | Placeholder text. |
| `button_text` | `'Browse…'` | Label of the browse button. |
| `disabled` | `False` | Start disabled. |

## Signals

- `file_selected(str)`: A path was chosen, the first one in multiple mode.
- `files_selected(list)`: All chosen paths.

## Public methods

- `browse()`: Open the native file dialog.
- `path() -> str`
- `paths() -> list[str]`
- `set_paths(paths)`: Set the selection and emit the signals.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import FilePicker, Stack

demo = Stack([FilePicker(filter="Images (*.png *.jpg)"), FilePicker(mode="directory", placeholder="No folder selected")])
```

## Usage guidance

- Files can also be dropped onto the control.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
