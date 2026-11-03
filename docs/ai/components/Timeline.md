# Timeline

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A vertical sequence of events.

Group: Data Display. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Timeline
```

## Signature

```python
Timeline(items=None, parent=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `items` | `None` | Dicts with title and optional description, time and variant (primary, neutral, success, warning, error or info). |
| `parent` | `None` | Parent widget. |

## Public methods

- `set_items(items)`: Replace the events.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Timeline

demo = Timeline([
    {"title": "Build passed", "description": "All 412 tests are green.", "time": "09:42", "variant": "success"},
    {"title": "Deploy started", "description": "Rolling out to production.", "time": "09:44"},
    {"title": "Latency warning", "description": "p95 rose above 400 ms.", "time": "09:51", "variant": "warning"},
    {"title": "Awaiting review", "time": "10:03", "variant": "neutral"},
])
```

## Usage guidance

- Order consistently, newest first for feeds and oldest first for processes.

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
