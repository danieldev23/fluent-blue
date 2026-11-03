from . import Entry

G = "Feedback"
ENTRIES = [
    Entry("Alert", G, '''
from fluent_blue import Alert, Stack

demo = Stack([
    Alert("Heads up", "A new version is available.", variant="info", action_text="Update"),
    Alert("Saved", "All changes are stored.", variant="success", closable=True),
    Alert("Storage almost full", "You have used 92% of your quota.", variant="warning"),
    Alert("Connection lost", "We will retry in 30 seconds.", variant="error", closable=True),
])
''', ["Use for persistent, in-context messages. Use Toast for passing confirmation."]),
    Entry("Toast", G, '''
from fluent_blue import Button, Stack, Toast

def button(text, variant):
    b = Button(text)
    b.clicked.connect(lambda: Toast.show(f"{text} toast message", parent=b, variant=variant))
    return b

demo = Stack([button("Info", "info"), button("Success", "success"), button("Warning", "warning"), button("Error", "error")],
             direction="horizontal")
''', ["Keep it to one sentence. People may not see it before it goes.", "Do not put errors requiring action here; use Alert or a dialog."]),
    Entry("Notification", G, '''
from fluent_blue import Button, Notification

demo = Button("Notify", icon="bell", variant="primary")
demo.clicked.connect(lambda: Notification.show("Export finished", "Your report is ready to download.", parent=demo,
                                               variant="success", action_text="Open"))
''', ["Use for events that deserve attention until acknowledged."]),
    Entry("Snackbar", G, '''
from fluent_blue import Button, Snackbar

demo = Button("Archive item", icon="archive")
demo.clicked.connect(lambda: Snackbar.show("Item archived", parent=demo, action_text="Undo"))
''', ["Prefer an undo over a confirmation dialog for reversible actions."]),
    Entry("MessageDialog", G, '''
from fluent_blue import Button, MessageDialog

demo = Button("Show message")

def show():
    MessageDialog(demo, title="Update installed", message="Restart the app to finish.", variant="success",
                  buttons=("Later", "Restart")).open()

demo.clicked.connect(show)
''', ["Interrupt only for information people must see now."]),
    Entry("ConfirmDialog", G, '''
from fluent_blue import ConfirmDialog, DangerButton, Toast

demo = DangerButton("Delete project", icon="trash")

def ask():
    dialog = ConfirmDialog(demo, title="Delete this project?", message="All its data is removed. This cannot be undone.",
                           confirm_text="Delete project", danger=True)
    dialog.confirmed.connect(lambda: Toast.show("Project deleted", parent=demo, variant="success"))
    dialog.open()

demo.clicked.connect(ask)
''', ["State the consequence, and label the button with the action, not “OK”."]),
    Entry("LoadingOverlay", G, '''
from fluent_blue import Button, Card, LoadingOverlay, Stack, Text
from fluent_blue.compatibility.qt import QTimer

card = Card(title="Quarterly report", subtitle="Overlay covers this card while it is busy.")
card.setMinimumHeight(110)
overlay = LoadingOverlay(card, message="Refreshing…")
start = Button("Load for 2 seconds", variant="primary")

def run():
    overlay.start()
    QTimer.singleShot(2000, overlay.stop)

start.clicked.connect(run)
demo = Stack([card, start], align="start", spacing=3)
''', ["Cover only the region that is busy, not the whole window."]),
    Entry("ProgressDialog", G, '''
from fluent_blue import Button, ProgressDialog
from fluent_blue.compatibility.qt import QTimer

demo = Button("Start export", icon="download", variant="primary")

def run():
    dialog = ProgressDialog(demo, title="Exporting", message="Writing 1,204 rows…")
    timer = QTimer(dialog)
    timer.setInterval(40)
    timer.timeout.connect(lambda: dialog.set_value(dialog.value() + 1))
    dialog.finished.connect(lambda _r: timer.stop())
    timer.start()
    dialog.open()

demo.clicked.connect(run)
''', ["Offer Cancel whenever the work can stop safely."]),
]
