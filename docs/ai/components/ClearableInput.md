# ClearableInput

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

An Input with the clear button on by default.

Group: Inputs. Qt base: `QLineEdit`, whose full API stays available.

## Import

```python
from fluent_blue import ClearableInput
```

## Signature

```python
ClearableInput(text='', parent=None, placeholder='', size='medium', prefix_icon=None, suffix_icon=None, clearable=False, validation='none', read_only=False, disabled=False, tooltip=None, accessible_name=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `text` | `''` | Initial text. |
| `parent` | `None` | Parent widget. |
| `placeholder` | `''` | Placeholder text. |
| `size` | `'medium'` | small, medium or large. |
| `prefix_icon` | `None` | Icon name at the start. |
| `suffix_icon` | `None` | Icon name at the end. |
| `clearable` | `False` | Show a clear button while the field has text. |
| `validation` | `'none'` | none, error, warning or success. |
| `read_only` | `False` | Selectable but not editable. |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |
| `accessible_name` | `None` | Name for assistive technology; defaults to the placeholder. |

## Signals

- `cleared()`: The clear button was used. Inherits textChanged, editingFinished and returnPressed from QLineEdit.

## Public methods

- `clear_text()`: Clear the field, emit cleared and keep focus.
- `set_validation(state: str)`: Set the validation state, which changes the border color.
- `validation() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import ClearableInput

demo = ClearableInput("Clear me", placeholder="Type something")
```

## Usage guidance

- Useful for filters and any value people often replace entirely.

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
