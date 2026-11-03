"""A large DataTable: 5,000 rows with renderers, column filters, selection and export."""
from __future__ import annotations

import random
import tempfile
from pathlib import Path

from fluent_blue import Button, Column, DataTable, Stack, Text, ThemeManager, Toast, badge_renderer, progress_renderer
from fluent_blue.compatibility.qt import QApplication, QWidget


def make_rows(count: int = 5000) -> list[dict]:
    rng = random.Random(7)
    names = ["Atlas", "Borealis", "Cirrus", "Delta", "Echo", "Fable", "Gemini", "Helix", "Ion", "Juno"]
    return [{
        "id": 1000 + i,
        "project": f"{rng.choice(names)} {rng.randint(1, 99)}",
        "status": rng.choice(["Active", "Paused", "Failed"]),
        "owner": rng.choice(["Ada", "Grace", "Alan", "Katherine"]),
        "progress": rng.randint(4, 100),
        "cost": round(rng.uniform(120, 9800), 2),
    } for i in range(count)]


def build() -> QWidget:
    table = DataTable([
        Column("id", "ID", width=80, align="right"),
        Column("project", width=170),
        Column("status", width=110, filterable=True, renderer=badge_renderer({"Active": "success", "Paused": "warning", "Failed": "error"})),
        Column("owner", width=110, filterable=True),
        Column("progress", width=170, renderer=progress_renderer()),
        Column("cost", align="right", formatter=lambda value: f"${value:,.2f}"),
    ], make_rows(), page_size=50, selection="multi", striped=True)

    export = Button("Export filtered rows to CSV", icon="download")

    def do_export() -> None:
        path = Path(tempfile.gettempdir()) / "fluent-blue-export.csv"
        count = table.export_csv(path)
        Toast.show(f"Exported {count} rows to {path}", parent=window, variant="success")

    export.clicked.connect(do_export)
    selected = Text("No rows selected", style="body-small", color="text-tertiary")
    table.selection_changed.connect(lambda rows: selected.setText(f"{len(rows)} selected" if rows else "No rows selected"))

    window = Stack([Text("Projects", style="heading-1"), Stack([export, selected], direction="horizontal", align="center"), table],
                   spacing=4, padding=6)
    window.layout().setStretch(2, 1)
    window.setWindowTitle("Data table")
    window.resize(1100, 720)
    return window


def main() -> int:
    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    window = build()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
