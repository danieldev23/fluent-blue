# IconButton

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A square icon-only button.

Group: Buttons. Qt base: `QPushButton`, whose full API stays available.

## Import

```python
from fluent_blue import IconButton
```

## Signature

```python
IconButton(icon, parent=None, variant=None, size='medium', tooltip=None, disabled=False, loading=False, checkable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `icon` | `required` | Icon name or QIcon. |
| `parent` | `None` | Parent widget. |
| `variant` | `None` | primary, secondary, outline, ghost, text or danger. |
| `size` | `'medium'` | small, medium or large. |
| `tooltip` | `None` | Also used as the accessible name, which an icon-only control needs. |
| `disabled` | `False` | Start disabled. |
| `loading` | `False` | Show a spinner and ignore clicks. |
| `checkable` | `False` | Toggle between checked and unchecked on each click. |

## Public methods

- `is_loading() -> bool`
- `set_full_width(full: bool)`
- `set_icon(icon: str | QIcon | None)`: Set the icon by name or QIcon; None removes it.
- `set_icon_position(position: str)`
- `set_loading(loading: bool)`: Show or hide the spinner. While loading, the button ignores clicks and keys.
- `set_size(size: str)`
- `set_variant(variant: str)`
- `size_name() -> str`
- `variant() -> str`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import IconButton, Stack

demo = Stack([
    IconButton("settings", tooltip="Settings"),
    IconButton("bell", variant="secondary", tooltip="Notifications"),
    IconButton("plus", variant="primary", tooltip="Add"),
    IconButton("trash", variant="danger", tooltip="Delete"),
    IconButton("star", size="small", tooltip="Favorite", checkable=True),
    IconButton("search", size="large", tooltip="Search"),
], direction="horizontal", align="center")
```

## Usage guidance

- Always set a tooltip; it doubles as the accessible name.
- Only use icons whose meaning is unambiguous.

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
