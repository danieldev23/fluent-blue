# CodeEditor

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A code editor with line numbers, syntax colors and smart indentation.

Group: Advanced Components. Qt base: `QPlainTextEdit`, whose full API stays available.

## Import

```python
from fluent_blue import CodeEditor
```

## Signature

```python
CodeEditor(text='', parent=None, language='python', read_only=False, line_numbers=True, tab_width=4)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `text` | `''` | Initial content. |
| `parent` | `None` | Parent widget. |
| `language` | `'python'` | python, json, sql or text. |
| `read_only` | `False` | Disable editing. |
| `line_numbers` | `True` | Show the gutter. |
| `tab_width` | `4` | Spaces per indent level. |

## Signals

- `code_changed(str)`: The content changed.

## Public methods

- `code() -> str`
- `gutter_width() -> int`
- `set_code(text: str)`
- `set_language(language: str)`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import CodeEditor

demo = CodeEditor("""from fluent_blue import ThemeManager

def toggle(window):
    # Switch theme at runtime
    name = ThemeManager.toggle()
    print(f"Now using {name}", 42)
""", language="python")
demo.setMinimumHeight(170)
```

## Usage guidance

- Tab inserts spaces, and Enter keeps the indentation level.
- Use read_only=True to display code.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
