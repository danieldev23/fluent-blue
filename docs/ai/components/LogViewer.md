# LogViewer

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A live log view with level filtering, search and tailing.

Group: Advanced Components. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import LogViewer
```

## Signature

```python
LogViewer(parent=None, max_entries=10000, timestamps=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `max_entries` | `10000` | Retained entries; the oldest are dropped first. |
| `timestamps` | `True` | Prefix each entry with its time. |

## Signals

- `entry_added(str, str)`: The message and level of a new entry.
- `record_received()`: 

## Public methods

- `attach_logger(logger: logging.Logger | None = None, level: int = 10) -> logging.Handler`: Route a logging logger here, thread-safely. Returns the handler to remove later.
- `clear()`
- `entries() -> list[tuple[str, str, str]]`: All retained entries as (time, level, message).
- `export(path) -> int`: Write visible entries to a text file and return the count.
- `log(message: str, level: str = info)`: Append an entry. level is debug, info, warning or error.
- `set_levels(levels)`: Show only these levels.
- `set_query(query: str)`: Show only entries containing this text.
- `visible_text() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import LogViewer

demo = LogViewer()
demo.log("Starting worker pool", "debug")
demo.log("Connected to database", "info")
demo.log("Slow query: 1840 ms", "warning")
demo.log("Failed to write cache entry", "error")
demo.setMinimumHeight(200)
```

## Usage guidance

- attach_logger routes Python logging here, safely from any thread.

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
