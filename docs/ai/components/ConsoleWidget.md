# ConsoleWidget

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A high-performance rich console / terminal widget for desktop tools and logging.

Group: Data Display. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import ConsoleWidget
```

## Signature

```python
ConsoleWidget(parent=None, max_lines=2000, show_toolbar=True, disabled=False, tooltip=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `max_lines` | `2000` | Max number of log lines to retain in memory (default 2000). |
| `show_toolbar` | `True` | Whether to render the quick action toolbar on top. |
| `disabled` | `False` | Start disabled. |
| `tooltip` | `None` | Tooltip text. |

## Signals

- `line_appended()`: 

## Public methods

- `clear()`: Clear all text in console.
- `copy_all()`: Copy all log content to system clipboard.
- `log(text: str, tag: str | None = None)`: Append a log line with optional timestamp and tag parsing.
- `to_plain_text() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import ConsoleWidget

demo = ConsoleWidget()
demo.log("Worker started")
demo.log("Job finished")
demo.setMinimumHeight(180)
```

## Usage guidance

- Use for tool and bot output. Use LogViewer when people need level filters and search.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
