# Calendar

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A month view. Arrow keys move, Enter selects and Page Up/Down change the month.

Group: Advanced Components. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Calendar
```

## Signature

```python
Calendar(parent=None, selected=None, minimum=None, maximum=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `selected` | `None` | Initially selected date. |
| `minimum` | `None` | Earliest selectable date. |
| `maximum` | `None` | Latest selectable date. |

## Signals

- `date_selected(object)`: The chosen datetime.date.
- `month_changed(int, int)`: The visible year and month.

## Public methods

- `cursor_date() -> dt.date`
- `first_visible_day() -> dt.date`: The Monday on or before the first of the visible month.
- `is_enabled_date(day: dt.date) -> bool`
- `select(day: dt.date)`: Select a date as if chosen by the user. Dates out of range are ignored.
- `selected_date() -> dt.date | None`
- `set_selected_date(day: dt.date | None)`: Select a date programmatically, without emitting date_selected.
- `shift_month(delta: int)`: Move the visible month.
- `visible_month() -> tuple[int, int]`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
import datetime as dt

from fluent_blue import Calendar

demo = Calendar(selected=dt.date(2026, 11, 4), minimum=dt.date(2026, 1, 1))
```

## Usage guidance

- Set minimum and maximum, so that invalid dates cannot be chosen at all.

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
