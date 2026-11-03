# Card

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A content container.

Group: Data Display. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Card
```

## Signature

```python
Card(parent=None, title='', subtitle='', elevation=0, tone='default', hoverable=False, clickable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `title` | `''` | Header title. |
| `subtitle` | `''` | Header subtitle. |
| `elevation` | `0` | Shadow level from 0 to 4. |
| `tone` | `'default'` | default, secondary or brand. |
| `hoverable` | `False` | Highlight the border on hover. |
| `clickable` | `False` | Make the card activatable by mouse and keyboard. |

## Signals

- `clicked()`: A clickable card was activated.

## Public methods

- `add(widget, stretch: int = 0)`: Add a widget to the content layout and return it.
- `content_layout() -> QVBoxLayout`: Return the card's layout with token padding, creating it if necessary.
- `set_elevation(level: int)`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Card, Grid, Text

demo = Grid(columns=3)
plain = demo.add(Card(title="Plain card", subtitle="Border only, for dense layouts."))
raised = demo.add(Card(title="Elevated", subtitle="Elevation level 2.", elevation=2))
click = demo.add(Card(title="Clickable", subtitle="Mouse and keyboard.", clickable=True))
brand = demo.add(Card(tone="brand", title="Brand tone", subtitle="Use sparingly."))
second = demo.add(Card(tone="secondary", title="Secondary tone", subtitle="A quieter surface."))
action = demo.add(Card(title="With content"))
action.add(Button("Open", variant="primary", size="small"))
```

## Usage guidance

- Prefer borders in dense views; shadows are for things that float.
- Avoid nesting cards.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
