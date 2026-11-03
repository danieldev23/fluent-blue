# RichTextEditor

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A rich text editor with a formatting toolbar.

Group: Advanced Components. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import RichTextEditor
```

## Signature

```python
RichTextEditor(parent=None, html='', placeholder='Write something…', read_only=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `html` | `''` | Initial HTML content. |
| `placeholder` | `'Write something…'` | Placeholder text. |
| `read_only` | `False` | Hide the toolbar and disable editing. |

## Signals

- `content_changed()`: The document changed.

## Public methods

- `clear_formatting()`: Remove character formatting from the selection.
- `insert_link(url: str, text: str | None = None)`: Insert a link at the cursor, using the selection as the label if there is one.
- `set_html(html: str)`
- `set_markdown(text: str)`
- `to_html() -> str`
- `to_markdown() -> str`
- `to_plain_text() -> str`
- `toggle_bold()`
- `toggle_italic()`
- `toggle_list(style)`: Turn the current blocks into a list, or remove them from the current list.
- `toggle_strike()`
- `toggle_underline()`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import RichTextEditor

demo = RichTextEditor(html="<p>Start writing <b>here</b>. Use the toolbar or <i>keyboard shortcuts</i>.</p>")
demo.setMinimumHeight(180)
```

## Usage guidance

- Store to_html or to_markdown, depending on what your backend needs.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
