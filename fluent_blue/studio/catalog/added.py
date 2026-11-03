from . import Entry

ENTRIES = [
    Entry("BadgeOverlay", "Data Display", '''
from fluent_blue import BadgeOverlay, IconButton, Stack

demo = Stack([
    BadgeOverlay(IconButton("bell", variant="secondary", tooltip="Notifications"), "3"),
    BadgeOverlay(IconButton("mail", variant="secondary", tooltip="Mail"), dot=True),
], direction="horizontal", spacing=4)
''', ["Show a count only when it needs attention, and hide the badge at zero."]),
    Entry("OtpInput", "Inputs", '''
from fluent_blue import OtpInput

demo = OtpInput()
''', ["Paste is supported, so people can drop in a whole code.", "Connect to completed, which fires once every digit is filled."]),
    Entry("TagInput", "Inputs", '''
from fluent_blue import TagInput

demo = TagInput()
demo.add_tag("design")
demo.add_tag("python")
''', ["Use for free-form labels; use MultiSelect when the options are a fixed list."]),
    Entry("ConsoleWidget", "Data Display", '''
from fluent_blue import ConsoleWidget

demo = ConsoleWidget()
demo.log("Worker started")
demo.log("Job finished")
demo.setMinimumHeight(180)
''', ["Use for tool and bot output. Use LogViewer when people need level filters and search."]),
    Entry("TitleBar", "Layout", '''
from fluent_blue import FluentWindow, TitleBar

window = FluentWindow(title="Example")
demo = window.findChild(TitleBar)
demo.setParent(None)
''', ["Usually created for you by FluentWindow."]),
    Entry("FluentWindow", "Layout", '''
from fluent_blue import Button, FluentWindow

launch = Button("Open window", icon="external-link", variant="primary")
window = FluentWindow(title="Fluent Blue Application")
window.set_central_widget(Button("Central content"))
window.resize(480, 280)
launch.clicked.connect(window.show)
demo = launch
''', ["Keep the keyboard shortcuts for closing the window working when you customize it."]),
]
