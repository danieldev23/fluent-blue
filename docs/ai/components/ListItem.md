# ListItem

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

One row of a list.

Group: Data Display. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import ListItem
```

## Signature

```python
ListItem(title='', parent=None, subtitle='', icon=None, leading=None, trailing=None, clickable=False, selected=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `title` | `''` | Primary text. |
| `parent` | `None` | Parent widget. |
| `subtitle` | `''` | Secondary text. |
| `icon` | `None` | Leading icon name. |
| `leading` | `None` | Leading widget, such as an Avatar. |
| `trailing` | `None` | Trailing widget, such as a Badge. |
| `clickable` | `False` | Make the row activatable by mouse and keyboard. |
| `selected` | `False` | Initial selected state. |

## Signals

- `clicked()`: A clickable row was activated.

## Public methods

- `is_selected() -> bool`
- `set_selected(selected: bool)`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Avatar, Badge, ListItem, Stack

demo = Stack([
    ListItem("Ada Lovelace", subtitle="Maintainer", leading=Avatar("Ada Lovelace"), trailing=Badge("Owner", variant="primary"), clickable=True),
    ListItem("Quarterly report.pdf", subtitle="2.4 MB", icon="file-text", clickable=True, selected=True),
    ListItem("Static row", subtitle="Not interactive", icon="info-circle"),
], spacing=1)
```

## Usage guidance

- Make the whole row the target, rather than a small control inside it.

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
