# Accordion

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A vertical stack of collapsible sections, optionally allowing only one open at a time.

Group: Layout. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Accordion
```

## Signature

```python
Accordion(parent=None, exclusive=False, spacing=2)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `exclusive` | `False` | Opening a section closes the others. |
| `spacing` | `2` | Spacing token step between sections. |

## Signals

- `expanded_changed(int, bool)`: The index of a section and whether it is now expanded.

## Public methods

- `add_item(title: str, content, *, expanded: bool = False) -> CollapsiblePanel`: Add a section holding content (a widget, or text) and return its panel.
- `collapse_all()`
- `count() -> int`
- `expand_all()`: Open every section. Ignored in exclusive mode.
- `is_expanded(index: int) -> bool`
- `set_expanded(index: int, expanded: bool)`: Expand or collapse a section; in exclusive mode opening one closes the rest.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Accordion, Text

demo = Accordion(exclusive=True)
demo.add_item("What is Fluent Blue?", "A design system for PyQt6 and PySide6 desktop applications.", expanded=True)
demo.add_item("Can I change the theme at runtime?", "Yes. ThemeManager.set_theme restyles every open window.")
demo.add_item("Does it work offline?", Text("It has no network code at all.", color="text-secondary"))
```

## Usage guidance

- Use exclusive=True for FAQs so that one answer is open at a time.
- Put long help text here, not essential form fields.

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
