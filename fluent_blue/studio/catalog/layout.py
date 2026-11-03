from . import Entry

G = "Layout"
ENTRIES = [
    Entry("Container", G, '''
from fluent_blue import Card, Container

demo = Container(max_width=420, padding=2)
demo.add(Card(title="Limited width", subtitle="Content stops growing at 420 px, which keeps line length readable."))
''', ["Wrap page content in it so that very wide monitors stay comfortable."]),
    Entry("Stack", G, '''
from fluent_blue import Badge, Button, Stack

row = Stack([Button("One"), Button("Two"), Button("Three")], direction="horizontal", spacing=2)
demo = Stack([row, Badge("Vertical stack, spacing token 3", variant="primary")], spacing=3, align="start")
''', ["Spacing takes token steps, which keeps the 4 px rhythm without magic numbers."]),
    Entry("Grid", G, '''
from fluent_blue import Card, Grid

demo = Grid(min_column_width=180)
for number in range(1, 7):
    demo.add(Card(title=f"Cell {number}", subtitle="Reflows with width."))
''', ["Set min_column_width for responsive layouts, or columns for a fixed one."]),
    Entry("Splitter", G, '''
from fluent_blue import Card, Splitter

demo = Splitter([Card(title="Navigator"), Card(title="Editor")], sizes=[180, 420])
demo.setFixedHeight(120)
''', ["Set sensible minimum sizes on panes so that they cannot be crushed."]),
    Entry("Panel", G, '''
from fluent_blue import IconButton, Panel, Text

demo = Panel("Details", actions=[IconButton("refresh", size="small", tooltip="Refresh"), IconButton("more-horizontal", size="small", tooltip="More")])
demo.add(Text("Panels have a header with an action area.", color="text-secondary"))
''', ["Use for tool regions in app layouts. Use Card for self-contained content."]),
    Entry("Drawer", G, '''
from fluent_blue import Button, Drawer, FormField, Input, Stack

demo = Stack([Button("Open drawer", icon="sidebar", variant="primary")], align="start")
trigger = demo.findChildren(Button)[0]

def open_drawer():
    drawer = Drawer(demo, title="Edit profile")
    drawer.add(FormField("Name", Input("Ada Lovelace")))
    drawer.add(Button("Save", variant="primary"))
    drawer.body.addStretch(1)
    drawer.closed.connect(drawer.deleteLater)
    drawer.open_drawer()

trigger.clicked.connect(open_drawer)
''', ["Use when people need to keep the page in view while they work."]),
    Entry("Modal", G, '''
from fluent_blue import Button, FormField, Input, Modal

demo = Button("Open modal", variant="primary")

def show():
    modal = Modal(demo, title="Rename project")
    modal.body.addWidget(FormField("Name", Input("Fluent Blue")))
    modal.add_action(Button("Cancel")).clicked.connect(modal.reject)
    modal.add_action(Button("Rename", variant="primary")).clicked.connect(modal.accept)
    modal.open()

demo.clicked.connect(show)
''', ["Modals stop everything, so keep them short and focused on one decision."]),
    Entry("CollapsiblePanel", G, '''
from fluent_blue import CollapsiblePanel, Stack, Text

one = CollapsiblePanel("Advanced settings")
one.add(Text("These options rarely need changing.", color="text-secondary"))
two = CollapsiblePanel("Diagnostics", expanded=False)
two.add(Text("Hidden until expanded.", color="text-secondary"))
demo = Stack([one, two])
''', ["Hide secondary options, but never required fields."]),
    Entry("ScrollArea", G, '''
from fluent_blue import ListItem, ScrollArea, Stack

demo = ScrollArea(Stack([ListItem(f"Row {n}", icon="file") for n in range(1, 21)], spacing=1))
demo.setFixedHeight(150)
''', ["Avoid nested vertical scrolling; it traps the mouse wheel."]),
]
