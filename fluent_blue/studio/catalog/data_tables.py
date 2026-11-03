from . import Entry

G = "Data Tables"
ENTRIES = [
    Entry("DataTable", G, '''
import random

from fluent_blue import Column, DataTable, badge_renderer, progress_renderer

rng = random.Random(7)
names = ["Atlas", "Borealis", "Cirrus", "Delta", "Echo", "Fable", "Gemini", "Helix", "Ion", "Juno"]
rows = [{
    "id": 1000 + i,
    "project": f"{rng.choice(names)} {rng.randint(1, 99)}",
    "status": rng.choice(["Active", "Paused", "Failed"]),
    "owner": rng.choice(["Ada", "Grace", "Alan", "Katherine"]),
    "progress": rng.randint(4, 100),
    "cost": round(rng.uniform(120, 9800), 2),
} for i in range(240)]

demo = DataTable([
    Column("id", "ID", width=80, align="right"),
    Column("project", width=170),
    Column("status", width=110, filterable=True,
           renderer=badge_renderer({"Active": "success", "Paused": "warning", "Failed": "error"})),
    Column("owner", width=110, filterable=True),
    Column("progress", width=170, renderer=progress_renderer()),
    Column("cost", align="right", formatter=lambda v: f"${v:,.2f}"),
], rows, page_size=8, selection="multi")
demo.setMinimumHeight(430)
''', ["Right-align numbers so that magnitudes line up.", "Use page_size=None only with a small row count, or keep a filter visible."]),
    Entry("Column", G, '''
from fluent_blue import Column, DataTable

demo = DataTable([
    Column("name", "Full name", width=200),
    Column("salary", align="right", formatter=lambda v: f"${v:,}"),
    Column("note", sortable=False, visible=False),
], [{"name": "Ada", "salary": 120000, "note": "hidden"}, {"name": "Grace", "salary": 134000, "note": "hidden"}],
    page_size=None, exportable=False)
demo.setMinimumHeight(190)
''', ["Formatters change only the display, so sorting still uses the raw value."]),
]
