# Kbd

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A keyboard shortcut drawn as key caps, such as Ctrl + K.

Group: Data Display. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import Kbd
```

## Signature

```python
Kbd(keys='', parent=None, size='medium')
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `keys` | `''` | A string such as "Ctrl+Shift+P", or a list of key names. |
| `parent` | `None` | Parent widget. |
| `size` | `'medium'` | small or medium. |

## Public methods

- `keys() -> list[str]`
- `set_keys(keys: str | list[str])`: Replace the keys. A string is split on +; spaces around names are ignored.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Kbd, Stack, Text

def line(label, keys):
    return Stack([Text(label, color="text-secondary"), Kbd(keys)], direction="horizontal", align="center", spacing=3)

demo = Stack([line("Command palette", "Ctrl+K"), line("Save", "Ctrl+S"), line("Reopen closed tab", "Ctrl+Shift+T"), Kbd("Esc", size="small")], spacing=3)
```

## Usage guidance

- Write modifiers in the order Ctrl, Alt, Shift, then the key.
- Use the platform's names, such as Cmd on macOS.

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
