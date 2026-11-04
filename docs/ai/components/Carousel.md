# Carousel

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A set of slides shown one at a time, with arrows, dots, keyboard and optional autoplay.

Group: Data Display. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Carousel
```

## Signature

```python
Carousel(parent=None, autoplay_ms=0, loop=True, show_arrows=True, show_dots=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `autoplay_ms` | `0` | Milliseconds between slides; 0 turns autoplay off. |
| `loop` | `True` | Wrap from the last slide to the first and back. |
| `show_arrows` | `True` | Show previous and next buttons. |
| `show_dots` | `True` | Show the page indicator. |

## Signals

- `current_changed(int)`: The index of the slide now shown.

## Public methods

- `add_slide(widget) -> int`: Add a slide and return its index.
- `count() -> int`
- `current() -> int`
- `is_playing() -> bool`
- `next()`
- `previous()`
- `set_autoplay(milliseconds: int)`: Change the autoplay interval; 0 stops autoplay.
- `set_current(index: int)`: Show a slide; out-of-range indexes are clamped, or wrapped when loop is on.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Card, Carousel, Text

demo = Carousel(autoplay_ms=0)
for number, (title, note) in enumerate((("Design tokens", "One source for every color and size."), ("Runtime themes", "Switch light and dark in about 80 ms."),
                                         ("Real components", "More than a hundred, all keyboard accessible.")), start=1):
    slide = Card(title=f"{number}. {title}", subtitle=note)
    slide.setMinimumHeight(120)
    demo.add_slide(slide)
```

## Usage guidance

- Autoplay pauses on hover, on focus and when hidden; never autoplay important content.
- Left and Right arrow keys change slides.
- Keep slides the same height to avoid the layout jumping.

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
