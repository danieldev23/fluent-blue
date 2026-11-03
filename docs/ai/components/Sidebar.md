# Sidebar

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A vertical, sectioned, collapsible navigation rail.

Group: Navigation. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Sidebar
```

## Signature

```python
Sidebar(parent=None, width=232, collapsed_width=56, tone='default')
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `width` | `232` | Expanded width in pixels. |
| `collapsed_width` | `56` | Width in the collapsed state. |
| `tone` | `'default'` | default, or brand for a blue gradient rail. |

## Signals

- `current_changed(str)`: The key of the newly selected item.
- `collapsed_changed(bool)`: The collapsed state changed.

## Public methods

- `add_item(text: str, *, key: str | None = None, icon: str | None = None, badge=None, disabled: bool = False) -> SidebarItem`: Add a navigation entry. The first entry added becomes current.
- `add_section(title: str) -> QLabel`: Add a section heading.
- `current() -> str | None`
- `is_collapsed() -> bool`
- `item(key: str) -> SidebarItem`
- `keys() -> list[str]`
- `set_collapsed(collapsed: bool)`: Collapse to an icon rail or expand, animated by motion tokens.
- `set_current(key: str)`: Select an item and emit current_changed.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Sidebar, Stack

sidebar = Sidebar(width=220)
sidebar.setFixedHeight(280)
sidebar.add_section("Workspace")
sidebar.add_item("Home", icon="home")
sidebar.add_item("Inbox", icon="inbox", badge=4)
sidebar.add_item("Projects", icon="layers")
sidebar.add_section("Account")
sidebar.add_item("Settings", icon="settings")
toggle = Button("Collapse", icon="sidebar", size="small")
toggle.clicked.connect(lambda: sidebar.set_collapsed(not sidebar.is_collapsed()))
demo = Stack([toggle, sidebar], direction="horizontal", align="start")
```

## Usage guidance

- Group items into sections with short headings.
- Connect current_changed to a QStackedWidget to swap pages.

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
