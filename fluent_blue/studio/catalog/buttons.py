from . import Entry

G = "Buttons"
ENTRIES = [
    Entry("Button", G, '''
from fluent_blue import Button, Stack

row = lambda *items: Stack(items, direction="horizontal", spacing=2, align="center")
demo = Stack([
    row(*[Button(v.title(), variant=v) for v in ("primary", "secondary", "outline", "ghost", "text", "danger")]),
    row(Button("Small", size="small", variant="primary"), Button("Medium", variant="primary"),
        Button("Large", size="large", variant="primary")),
    row(Button("Add item", icon="plus", variant="primary"), Button("Next", icon="arrow-right", icon_position="right"),
        Button("Disabled", disabled=True), Button("Saving", loading=True, variant="primary")),
    Button("Full width", variant="outline", full_width=True),
], spacing=3)
''', ["Use one primary button per view; it marks the main path.", "Label buttons with a verb that names the outcome, such as “Save changes”."]),
    Entry("PrimaryButton", G, '''
from fluent_blue import PrimaryButton, Stack

demo = Stack([PrimaryButton("Create project", icon="plus"), PrimaryButton("Disabled", disabled=True)],
             direction="horizontal")
''', ["Reserve it for the action most users came to do.", "Pair it with a secondary button for the alternative."]),
    Entry("SecondaryButton", G, '''
from fluent_blue import SecondaryButton, Stack

demo = Stack([SecondaryButton("Export", icon="download"), SecondaryButton("Disabled", disabled=True)],
             direction="horizontal")
''', ["The right default for most actions.", "Several can sit side by side without competing."]),
    Entry("OutlineButton", G, '''
from fluent_blue import OutlineButton, Stack

demo = Stack([OutlineButton("Invite people", icon="user-plus"), OutlineButton("Disabled", disabled=True)],
             direction="horizontal")
''', ["Use for a brand-tinted action that should not outrank the primary button."]),
    Entry("GhostButton", G, '''
from fluent_blue import GhostButton, Stack

demo = Stack([GhostButton("Edit", icon="edit"), GhostButton("Share", icon="share"), GhostButton("Disabled", disabled=True)],
             direction="horizontal")
''', ["Best in toolbars and dense rows, where borders would add noise."]),
    Entry("TextButton", G, '''
from fluent_blue import Stack, Text, TextButton

demo = Stack([Text("Need more detail?"), TextButton("Read the guide", icon="external-link", icon_position="right")],
             direction="horizontal", align="center")
''', ["Use inline with content, like a link that triggers an action."]),
    Entry("DangerButton", G, '''
from fluent_blue import DangerButton, Stack

demo = Stack([DangerButton("Delete project", icon="trash"), DangerButton("Disabled", disabled=True)],
             direction="horizontal")
''', ["Confirm irreversible actions with a ConfirmDialog.", "Name what is destroyed, not just “Delete”."]),
    Entry("IconButton", G, '''
from fluent_blue import IconButton, Stack

demo = Stack([
    IconButton("settings", tooltip="Settings"),
    IconButton("bell", variant="secondary", tooltip="Notifications"),
    IconButton("plus", variant="primary", tooltip="Add"),
    IconButton("trash", variant="danger", tooltip="Delete"),
    IconButton("star", size="small", tooltip="Favorite", checkable=True),
    IconButton("search", size="large", tooltip="Search"),
], direction="horizontal", align="center")
''', ["Always set a tooltip; it doubles as the accessible name.", "Only use icons whose meaning is unambiguous."]),
    Entry("LoadingButton", G, '''
from fluent_blue import LoadingButton
from fluent_blue.compatibility.qt import QTimer

demo = LoadingButton("Save changes", loading_text="Saving…")

def save():
    demo.start()
    QTimer.singleShot(1500, demo.stop)

demo.clicked.connect(save)
''', ["Keep the button's width stable by using a similar loading label.", "Clicks are ignored while loading, so double submission cannot happen."]),
    Entry("SplitButton", G, '''
from fluent_blue import SplitButton

demo = SplitButton("Save", icon="save", items=[
    {"text": "Save as…", "icon": "file"},
    {"text": "Save a copy", "icon": "copy"},
    None,
    {"text": "Discard", "icon": "trash", "danger": True},
])
''', ["The main action should be what most people want most of the time.", "Menu entries should be variations of the same task."]),
]
