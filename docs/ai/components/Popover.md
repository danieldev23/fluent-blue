# Popover

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A floating panel anchored to a widget. It closes on outside click or Escape.

Group: Data Display. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Popover
```

## Signature

```python
Popover(parent=None, title='', content=None, width=280)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Owner widget. |
| `title` | `''` | Optional heading. |
| `content` | `None` | Text or a widget. |
| `width` | `280` | Panel width in pixels. |

## Signals

- `closed()`: The popover was hidden.

## Public methods

- `show_at(anchor, placement: str = bottom, gap: int = 4)`: Show next to anchor (top, bottom, left, right), kept on screen.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Popover

demo = Button("Show details", icon="info-circle")
pop = Popover(demo, title="About this metric", content="Sessions counted over the trailing 28 days, excluding internal traffic.")
demo.clicked.connect(lambda: pop.show_at(demo))
```

## Usage guidance

- Use for rich, secondary content on demand. Use Modal when a decision is required.

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
