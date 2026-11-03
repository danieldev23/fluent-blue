# CommandPalette

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A searchable command launcher.

Group: Navigation. Qt base: `QDialog`, whose full API stays available.

## Import

```python
from fluent_blue import CommandPalette
```

## Signature

```python
CommandPalette(parent=None, commands=None, shortcut='Ctrl+K', placeholder='Type a command or search…')
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Window the palette opens over and listens on for the shortcut. |
| `commands` | `None` | Initial Command objects. |
| `shortcut` | `'Ctrl+K'` | Global shortcut, or None for none. |
| `placeholder` | `'Type a command or search…'` | Search placeholder. |

## Signals

- `command_triggered(str)`: The id of the chosen command.

## Public methods

- `add_command(command: Command)`: Add a command.
- `open_palette()`: Show the palette centered near the top of its parent window.
- `run(command_id: str)`: Run a command by id.
- `set_commands(commands)`: Replace all commands.
- `visible_ids() -> list[str]`: Ids currently listed, in display order.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Button, Command, CommandPalette, Toast

demo = Button("Open command palette", icon="search", variant="primary")
palette = CommandPalette(demo, shortcut=None, commands=[
    Command("new", "New project", "Create an empty project", "plus"),
    Command("theme", "Switch theme", "Light or dark", "palette"),
    Command("docs", "Open documentation", icon="file-text"),
])
palette.command_triggered.connect(lambda cid: Toast.show(f"Ran: {cid}", parent=demo, variant="success"))
demo.clicked.connect(palette.open_palette)
```

## Usage guidance

- Pass a window as the parent and keep the default Ctrl+K shortcut.
- Add keywords, because people search with their own words.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
