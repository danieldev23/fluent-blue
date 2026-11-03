from . import Entry

G = "Data Display"
ENTRIES = [
    Entry("Card", G, '''
from fluent_blue import Button, Card, Grid, Text

demo = Grid(columns=3)
plain = demo.add(Card(title="Plain card", subtitle="Border only, for dense layouts."))
raised = demo.add(Card(title="Elevated", subtitle="Elevation level 2.", elevation=2))
click = demo.add(Card(title="Clickable", subtitle="Mouse and keyboard.", clickable=True))
brand = demo.add(Card(tone="brand", title="Brand tone", subtitle="Use sparingly."))
second = demo.add(Card(tone="secondary", title="Secondary tone", subtitle="A quieter surface."))
action = demo.add(Card(title="With content"))
action.add(Button("Open", variant="primary", size="small"))
''', ["Prefer borders in dense views; shadows are for things that float.", "Avoid nesting cards."]),
    Entry("StatisticCard", G, '''
from fluent_blue import Grid, StatisticCard

demo = Grid(columns=3)
demo.add(StatisticCard("Revenue", "$48.2k", delta="+12.4%", trend="up", caption="vs last month", icon="chart-line",
                       spark=[3, 4, 3.6, 5, 4.8, 6, 7.2]))
demo.add(StatisticCard("Active users", "2,840", delta="+3.1%", trend="up", caption="vs last week", icon="users",
                       spark=[6, 5.8, 6.2, 6, 6.4, 6.6, 6.5]))
demo.add(StatisticCard("Error rate", "0.42%", delta="-0.08%", trend="down", caption="vs yesterday", icon="alert-triangle",
                       positive_is_up=False, spark=[5, 4.6, 4.8, 3.9, 3.2, 3.4, 2.9]))
''', ["Always give the number a comparison; a lone figure says little.", "Set positive_is_up=False for metrics where lower is better."]),
    Entry("Text", G, '''
from fluent_blue import Stack, Text

demo = Stack([
    Text("Display heading", style="heading-1"),
    Text("Body text in a secondary color.", color="text-secondary"),
    Text("Caption with tertiary color", style="caption", color="text-tertiary"),
    Text("print('monospace')", style="monospace", color="primary-text"),
], spacing=1)
''', ["Use typography roles, never ad hoc sizes, so that hierarchy stays consistent."]),
    Entry("Badge", G, '''
from fluent_blue import Badge, Stack

demo = Stack([Badge(v.title(), variant=v) for v in ("neutral", "primary", "success", "warning", "error", "info")]
             + [Badge("Online", variant="success", dot=True)], direction="horizontal", align="center")
''', ["Keep text to one or two words.", "Do not rely on color alone; the label carries the meaning."]),
    Entry("Tag", G, '''
from fluent_blue import Stack, Tag

demo = Stack([Tag("Design"), Tag("Python", variant="primary"), Tag("Stable", variant="success"),
              Tag("Beta", variant="warning"), Tag("Removable", closable=True)], direction="horizontal", align="center")
''', ["Use tags for categories that people add or remove; use badges for status."]),
    Entry("Avatar", G, '''
from fluent_blue import Avatar, Stack

demo = Stack([Avatar("Ada Lovelace", size="small"), Avatar("Grace Hopper", status="online"),
              Avatar("Alan Turing", size="large", status="busy"), Avatar("Linus Pauling", size="xl", status="away"),
              Avatar("Team Rocket", size="large", shape="square")], direction="horizontal", align="center")
''', ["Colors are derived from the name, so one person always looks the same."]),
    Entry("AvatarGroup", G, '''
from fluent_blue import AvatarGroup

demo = AvatarGroup(["Ada Lovelace", "Grace Hopper", "Alan Turing", "Katherine Johnson", "Tim Berners", "Edsger Dijkstra"],
                   max_visible=4)
''', ["The accessible name lists everyone, including those in the overflow."]),
    Entry("Divider", G, '''
from fluent_blue import Divider, Stack, Text

demo = Stack([Text("Above"), Divider(), Text("Between"), Divider("OR"), Text("Below")], spacing=2)
''', ["Prefer whitespace first; add a divider only when grouping is still unclear."]),
    Entry("Tooltip", G, '''
from fluent_blue import Button, Stack, Tooltip

top, bottom = Button("Hover: top"), Button("Hover: bottom")
Tooltip(top, "Appears above the control")
Tooltip(bottom, "Appears below the control", placement="bottom")
demo = Stack([top, bottom], direction="horizontal")
''', ["Tooltips supplement a label; they never hold essential information."]),
    Entry("Popover", G, '''
from fluent_blue import Button, Popover

demo = Button("Show details", icon="info-circle")
pop = Popover(demo, title="About this metric", content="Sessions counted over the trailing 28 days, excluding internal traffic.")
demo.clicked.connect(lambda: pop.show_at(demo))
''', ["Use for rich, secondary content on demand. Use Modal when a decision is required."]),
    Entry("ProgressBar", G, '''
from fluent_blue import ProgressBar, Stack

demo = Stack([ProgressBar(35), ProgressBar(68, show_label=True), ProgressBar(100, variant="success", show_label=True),
              ProgressBar(82, variant="warning", show_label=True), ProgressBar(indeterminate=True)], spacing=3)
''', ["Prefer a determinate bar whenever progress can be measured."]),
    Entry("CircularProgress", G, '''
from fluent_blue import CircularProgress, Stack

demo = Stack([CircularProgress(25), CircularProgress(72, variant="success"), CircularProgress(90, variant="warning", size=64),
              CircularProgress(indeterminate=True, size=32, thickness=3)], direction="horizontal", align="center", spacing=4)
''', ["Use in compact spaces, or as a spinner with indeterminate=True."]),
    Entry("Skeleton", G, '''
from fluent_blue import Skeleton, Stack

demo = Stack([Skeleton(shape="circle", width=48), Skeleton(lines=3)], direction="horizontal", spacing=4)
''', ["Mirror the layout of the content that will replace it, to limit layout shift."]),
    Entry("EmptyState", G, '''
from fluent_blue import EmptyState

demo = EmptyState("No projects yet", description="Projects keep your palettes and tokens together. Create one to get started.",
                  icon="layers", action_text="Create project")
''', ["Explain what will appear here, then offer the next step."]),
    Entry("Result", G, '''
from fluent_blue import Grid, Result

demo = Grid(columns=2)
demo.add(Result("success", "Payment received", description="A receipt is on its way.", action_text="View order"))
demo.add(Result("error", "Sync failed", description="We could not reach the server.", action_text="Try again"))
''', ["Say what happened and what to do next. Avoid raw error codes."]),
    Entry("Timeline", G, '''
from fluent_blue import Timeline

demo = Timeline([
    {"title": "Build passed", "description": "All 412 tests are green.", "time": "09:42", "variant": "success"},
    {"title": "Deploy started", "description": "Rolling out to production.", "time": "09:44"},
    {"title": "Latency warning", "description": "p95 rose above 400 ms.", "time": "09:51", "variant": "warning"},
    {"title": "Awaiting review", "time": "10:03", "variant": "neutral"},
])
''', ["Order consistently, newest first for feeds and oldest first for processes."]),
    Entry("ListItem", G, '''
from fluent_blue import Avatar, Badge, ListItem, Stack

demo = Stack([
    ListItem("Ada Lovelace", subtitle="Maintainer", leading=Avatar("Ada Lovelace"), trailing=Badge("Owner", variant="primary"), clickable=True),
    ListItem("Quarterly report.pdf", subtitle="2.4 MB", icon="file-text", clickable=True, selected=True),
    ListItem("Static row", subtitle="Not interactive", icon="info-circle"),
], spacing=1)
''', ["Make the whole row the target, rather than a small control inside it."]),
]
