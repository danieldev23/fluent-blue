# Quick start and tutorial

## Quick start

```python
from fluent_blue import Badge, Button, Card, Input, ThemeManager
from fluent_blue.compatibility.qt import QApplication, QVBoxLayout, QWidget

app = QApplication([])
ThemeManager.set_theme("light")

window = QWidget()
layout = QVBoxLayout(window)

card = Card()
card_layout = QVBoxLayout(card)
card_layout.addWidget(Input(placeholder="Enter your name..."))
card_layout.addWidget(Button("Get Started", variant="primary", size="large"))
card_layout.addWidget(Badge("New", variant="success"))

layout.addWidget(card)
window.show()
app.exec()
```

Two conventions make the rest of the library predictable:

- Import components from `fluent_blue`, and Qt classes from `fluent_blue.compatibility.qt`, which re-exports whichever binding is active. The same file runs on PyQt6 and PySide6.
- Fluent Blue's own methods and signals are `snake_case` (`set_value`, `value_changed`). Everything inherited from Qt keeps its `camelCase` name (`setText`, `clicked`), so the full Qt API is still there.

## Tutorial: a Projects app in five steps

The finished file is [`examples/projects_app.py`](examples.md). It is run by the test suite, so it cannot drift from the library.

### 1. The shell

A `Sidebar` on the left and a `QStackedWidget` on the right is the shape of most desktop tools. `Sidebar` groups items into sections, shows badges, collapses to an icon rail and reports the current key.

```python
from fluent_blue import Sidebar, ThemeManager
from fluent_blue.compatibility.qt import QHBoxLayout, QStackedWidget, QWidget

root = QWidget()
row = QHBoxLayout(root)
row.setContentsMargins(0, 0, 0, 0)

sidebar = Sidebar(width=220)
sidebar.add_section("Workspace")
sidebar.add_item("Projects", icon="layers")
sidebar.add_item("Settings", icon="settings")

pages = QStackedWidget()
row.addWidget(sidebar)
row.addWidget(pages, 1)
sidebar.current_changed.connect(lambda key: pages.setCurrentIndex(sidebar.keys().index(key)))
```

### 2. A page with real data

`DataTable` is built on Qt's model/view framework. Sorting, a search field, per-column filters, paging, multi-selection that survives page changes, column visibility, a context menu and CSV or JSON export are built in. Cell renderers draw status pills and progress bars without creating widgets per cell, so 100,000 rows stay fast.

```python
from fluent_blue import Column, DataTable, badge_renderer, progress_renderer

rows = [{"name": "Atlas", "status": "Active", "progress": 72}, {"name": "Borealis", "status": "Paused", "progress": 18}]
table = DataTable([
    Column("name", width=200),
    Column("status", width=120, filterable=True, renderer=badge_renderer({"Active": "success", "Paused": "warning"})),
    Column("progress", renderer=progress_renderer()),
], rows, page_size=25, selection="single")
```

### 3. Editing in a drawer

`FormField` adds a label, helper text, a required marker and validation to any input. A `Drawer` slides in from the edge of the window and keeps the table in view.

```python
from fluent_blue import Button, Drawer, FormField, Input

def edit(row):
    drawer = Drawer(root, title=f"Edit {row['name']}")
    name = FormField("Name", Input(row["name"]), required=True,
                     validator=lambda value: None if value.strip() else "A name is required.")
    drawer.add(name)
    save = drawer.add(Button("Save", variant="primary"))
    drawer.body.addStretch(1)
    save.clicked.connect(lambda: name.validate() and drawer.close_drawer())
    drawer.open_drawer()

table.row_activated.connect(edit)
```

### 4. Feedback that fits the moment

Use a `Toast` for passing confirmation, a `ConfirmDialog` before anything destructive, and a `Snackbar` with an undo for actions that can be reversed.

```python
from fluent_blue import ConfirmDialog, Snackbar, Toast

def archive():
    if ConfirmDialog.ask(root, "Archive selected projects?", "You can restore them from the archive.", confirm_text="Archive"):
        Snackbar.show("Projects archived", parent=root, action_text="Undo", on_action=lambda: Toast.show("Restored", parent=root))
```

### 5. Theme and ship

Themes apply to every open widget at runtime. `"system"` follows the operating system and reacts when it changes.

```python
ThemeManager.set_theme("dark")        # or "light", "high-contrast", "system"
ThemeManager.register_theme("brand", {"base": "light", "colors": {"primary": "#7C3AED"}})
ThemeManager.set_theme("brand")       # the full primary ramp is derived from one color
```

## Where next

- [Components](components/index.md) for every component with a screenshot and its API.
- [Theming](theming.md) for custom themes, tokens and theme-aware custom widgets.
- [Examples](examples.md) for complete applications.
