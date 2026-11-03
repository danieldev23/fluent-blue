"""The README tutorial: a small Projects app with a sidebar, a data table, a drawer form and feedback.

Run it with ``python examples/projects_app.py``. ``build()`` returns the root widget so that
the test suite can construct it headlessly.
"""
from __future__ import annotations

from fluent_blue import (
    Button,
    Column,
    ConfirmDialog,
    DataTable,
    Drawer,
    FormField,
    Input,
    Sidebar,
    Snackbar,
    Stack,
    Text,
    ThemeManager,
    Toast,
    badge_renderer,
    progress_renderer,
)
from fluent_blue.compatibility.qt import QApplication, QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget

ROWS = [
    {"name": "Atlas", "owner": "Ada", "status": "Active", "progress": 72},
    {"name": "Borealis", "owner": "Grace", "status": "Paused", "progress": 18},
    {"name": "Cirrus", "owner": "Alan", "status": "Active", "progress": 94},
    {"name": "Delta", "owner": "Katherine", "status": "Failed", "progress": 41},
]


def build() -> QWidget:
    # 1. The shell: a sidebar and a stack of pages.
    root = QWidget()
    root.setWindowTitle("Projects")
    row = QHBoxLayout(root)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(0)
    sidebar = Sidebar(width=220)
    sidebar.add_section("Workspace")
    sidebar.add_item("Projects", icon="layers")
    sidebar.add_item("Settings", icon="settings")
    pages = QStackedWidget()
    row.addWidget(sidebar)
    row.addWidget(pages, 1)
    sidebar.current_changed.connect(lambda key: pages.setCurrentIndex(sidebar.keys().index(key)))

    # 2. A page with real data.
    table = DataTable([
        Column("name", width=200),
        Column("owner", width=140, filterable=True),
        Column("status", width=120, filterable=True, renderer=badge_renderer({"Active": "success", "Paused": "warning", "Failed": "error"})),
        Column("progress", renderer=progress_renderer()),
    ], ROWS, page_size=25, selection="multi")

    # 3. Editing in a drawer.
    def edit(row: dict) -> None:
        drawer = Drawer(root, title=f"Edit {row['name']}")
        name = FormField("Name", Input(row["name"]), required=True,
                         validator=lambda value: None if value.strip() else "A name is required.")
        drawer.add(name)
        save = drawer.add(Button("Save", variant="primary"))
        drawer.body.addStretch(1)

        def commit() -> None:
            if name.validate():
                row["name"] = name.control.text()
                table.set_rows(table.rows())
                drawer.close_drawer()
                Toast.show("Project saved", parent=root, variant="success")

        save.clicked.connect(commit)
        drawer.closed.connect(drawer.deleteLater)
        drawer.open_drawer()

    table.row_activated.connect(edit)

    # 4. Feedback that fits the moment.
    def archive() -> None:
        selected = table.selected_rows()
        if not selected:
            Toast.show("Select a project first", parent=root, variant="warning")
            return
        if ConfirmDialog.ask(root, "Archive selected projects?", "You can restore them from the archive.", confirm_text="Archive"):
            kept = [row for row in table.rows() if row not in selected]
            table.set_rows(kept)
            Snackbar.show(f"{len(selected)} archived", parent=root, action_text="Undo",
                          on_action=lambda: (table.set_rows(ROWS), Toast.show("Restored", parent=root)))

    archive_button = Button("Archive selected", icon="archive")
    archive_button.clicked.connect(archive)
    projects = Stack([Text("Projects", style="heading-1"), Stack([archive_button], direction="horizontal"), table], spacing=4, padding=6)
    projects.layout().setStretch(2, 1)
    pages.addWidget(projects)

    # 5. Theme and ship.
    settings = QWidget()
    column = QVBoxLayout(settings)
    column.setContentsMargins(24, 24, 24, 24)
    column.addWidget(Text("Settings", style="heading-1"))
    toggle = Button("Toggle dark mode", icon="moon")
    toggle.clicked.connect(ThemeManager.toggle)
    column.addWidget(toggle)
    column.addStretch(1)
    pages.addWidget(settings)
    root.resize(1100, 700)
    return root


def main() -> int:
    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    window = build()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
