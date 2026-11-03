# TagInput

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

An input field that converts typed text into removable tags on Enter or comma.

Group: Inputs. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import TagInput
```

## Signature

```python
TagInput(parent=None, tags=None, placeholder='Type and press Enter...', max_tags=None, disabled=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `tags` | `None` | Initial list of string tags. |
| `placeholder` | `'Type and press Enter...'` | Placeholder text when empty. |
| `max_tags` | `None` | Maximum allowable tags. |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- `tags_changed(list)`: List of all tags after add/remove.
- `tag_added(str)`: The added tag.
- `tag_removed(str)`: The removed tag.

## Public methods

- `add_tag(tag: str) -> bool`: Add a new tag if not already present.
- `clear()`
- `remove_tag(tag: str) -> bool`: Remove an existing tag.
- `tags() -> list[str]`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import TagInput

demo = TagInput()
demo.add_tag("design")
demo.add_tag("python")
```

## Usage guidance

- Use for free-form labels; use MultiSelect when the options are a fixed list.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
