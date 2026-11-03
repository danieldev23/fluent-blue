from . import Entry

G = "Navigation"
ENTRIES = [
    Entry("Sidebar", G, '''
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
''', ["Group items into sections with short headings.", "Connect current_changed to a QStackedWidget to swap pages."]),
    Entry("SidebarItem", G, '''
from fluent_blue import SidebarItem, Stack

demo = Stack([SidebarItem("Dashboard", icon="dashboard"), SidebarItem("Messages", icon="message", badge=12),
              SidebarItem("Disabled", icon="ban", disabled=True)], spacing=1)
demo.setFixedWidth(220)
''', ["Usually created through Sidebar.add_item.", "Use the badge for counts that need attention."]),
    Entry("NavigationBar", G, '''
from fluent_blue import Avatar, IconButton, NavigationBar, SearchInput

demo = NavigationBar("Acme Console")
demo.add_center(SearchInput(size="small"))
demo.add_end(IconButton("bell", tooltip="Notifications"))
demo.add_end(Avatar("Ada Lovelace", status="online"))
''', ["Keep global actions here, and page actions in the page header."]),
    Entry("Breadcrumb", G, '''
from fluent_blue import Breadcrumb

demo = Breadcrumb(["Home", "Projects", "Fluent Blue", "Settings"])
''', ["Show where the current page sits in a deep hierarchy, not the history."]),
    Entry("Tabs", G, '''
from fluent_blue import Tabs, Text

demo = Tabs()
demo.add_tab(Text("Overview content", color="text-secondary"), "Overview", icon="home")
demo.add_tab(Text("Activity content", color="text-secondary"), "Activity", icon="clock")
demo.add_tab(Text("Settings content", color="text-secondary"), "Settings", icon="settings")
demo.setMinimumHeight(110)
''', ["Each tab should be a peer view of the same subject."]),
    Entry("TabBar", G, '''
from fluent_blue import TabBar

demo = TabBar(["All", "Open", "Closed", "Archived"])
''', ["Use the bare strip to drive your own content, such as a filtered list."]),
    Entry("Pagination", G, '''
from fluent_blue import Pagination

demo = Pagination(total=1280, page_size=20, page=7)
''', ["Show the range so people know how much data exists."]),
    Entry("Menu", G, '''
from fluent_blue import Button, Menu

demo = Button("Open menu", icon="menu")
menu = Menu(demo, items=[
    {"text": "New file", "icon": "file", "shortcut": "Ctrl+N"},
    {"text": "Open…", "icon": "folder-open", "shortcut": "Ctrl+O"},
    None,
    {"text": "Export", "items": ["PDF", "CSV", "JSON"]},
    {"text": "Show hidden files", "checkable": True, "checked": True},
    None,
    {"text": "Delete", "icon": "trash", "danger": True},
])
demo.clicked.connect(lambda: menu.popup(demo.mapToGlobal(demo.rect().bottomLeft())))
''', ["Keep menus short and put destructive entries last, after a separator."]),
    Entry("MenuItem", G, '''
from fluent_blue import Button, Menu, MenuItem

demo = Button("Sort by")
menu = Menu(demo)
menu.add_item(MenuItem("Name", menu, icon="type", checkable=True, checked=True))
menu.add_item(MenuItem("Date", menu, icon="calendar", checkable=True))
demo.setMenu(menu)
''', ["Create one directly for full control, such as keeping a reference to toggle it."]),
    Entry("DropdownMenu", G, '''
from fluent_blue import DropdownMenu

demo = DropdownMenu("Actions", items=[
    {"text": "Rename", "icon": "edit"},
    {"text": "Duplicate", "icon": "copy"},
    None,
    {"text": "Archive", "icon": "archive"},
], icon="zap")
''', ["Connect item_triggered and branch on the item id."]),
    Entry("CommandPalette", G, '''
from fluent_blue import Button, Command, CommandPalette, Toast

demo = Button("Open command palette", icon="search", variant="primary")
palette = CommandPalette(demo, shortcut=None, commands=[
    Command("new", "New project", "Create an empty project", "plus"),
    Command("theme", "Switch theme", "Light or dark", "palette"),
    Command("docs", "Open documentation", icon="file-text"),
])
palette.command_triggered.connect(lambda cid: Toast.show(f"Ran: {cid}", parent=demo, variant="success"))
demo.clicked.connect(palette.open_palette)
''', ["Pass a window as the parent and keep the default Ctrl+K shortcut.", "Add keywords, because people search with their own words."]),
]
