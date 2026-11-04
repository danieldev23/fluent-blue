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
    Entry("Rating", "Selection", '''
from fluent_blue import Rating, Stack, Text, Toast

live = Rating(3)
caption = Text("3 of 5", color="text-secondary")
live.value_changed.connect(lambda value: caption.setText(f"{value:g} of 5"))
demo = Stack([
    Stack([live, caption], direction="horizontal", align="center", spacing=3),
    Rating(3.5, allow_half=True, size=26),
    Rating(4, read_only=True, size=18),
], spacing=3)
''', ["Use half stars only when the average is shown with that precision.", "Clicking the current value again clears it; pass allow_clear=False to prevent that.",
        "Set read_only=True to display an average rating."]),
    Entry("RangeSlider", "Selection", '''
from fluent_blue import RangeSlider, Stack, Text

readout = Text("Price: $200 to $800", color="text-secondary")
slider = RangeSlider(200, 800, minimum=0, maximum=1000, step=50)
slider.range_changed.connect(lambda low, high: readout.setText(f"Price: ${low} to ${high}"))
demo = Stack([slider, readout], spacing=2)
''', ["Show the chosen range in text next to the slider.", "Use step to avoid meaningless precision.",
        "Up and Down choose the handle, Left and Right move it."]),
    Entry("Accordion", "Layout", '''
from fluent_blue import Accordion, Text

demo = Accordion(exclusive=True)
demo.add_item("What is Fluent Blue?", "A design system for PyQt6 and PySide6 desktop applications.", expanded=True)
demo.add_item("Can I change the theme at runtime?", "Yes. ThemeManager.set_theme restyles every open window.")
demo.add_item("Does it work offline?", Text("It has no network code at all.", color="text-secondary"))
''', ["Use exclusive=True for FAQs so that one answer is open at a time.", "Put long help text here, not essential form fields."]),
    Entry("Carousel", "Data Display", '''
from fluent_blue import Card, Carousel, Text

demo = Carousel(autoplay_ms=0)
for number, (title, note) in enumerate((("Design tokens", "One source for every color and size."), ("Runtime themes", "Switch light and dark in about 80 ms."),
                                         ("Real components", "More than a hundred, all keyboard accessible.")), start=1):
    slide = Card(title=f"{number}. {title}", subtitle=note)
    slide.setMinimumHeight(120)
    demo.add_slide(slide)
''', ["Autoplay pauses on hover, on focus and when hidden; never autoplay important content.", "Left and Right arrow keys change slides.",
        "Keep slides the same height to avoid the layout jumping."]),
    Entry("Kbd", "Data Display", '''
from fluent_blue import Kbd, Stack, Text

def line(label, keys):
    return Stack([Text(label, color="text-secondary"), Kbd(keys)], direction="horizontal", align="center", spacing=3)

demo = Stack([line("Command palette", "Ctrl+K"), line("Save", "Ctrl+S"), line("Reopen closed tab", "Ctrl+Shift+T"), Kbd("Esc", size="small")], spacing=3)
''', ["Write modifiers in the order Ctrl, Alt, Shift, then the key.", "Use the platform's names, such as Cmd on macOS."]),
    Entry("VideoPlayer", "Advanced Components", '''
from fluent_blue import VideoPlayer

demo = VideoPlayer()  # Pass a path or URL, or press "Open video…": VideoPlayer("clip.mp4", autoplay=True)
demo.setMinimumHeight(300)
''', ["Space plays and pauses, Left and Right seek five seconds, Up and Down change the volume, M mutes and F toggles full screen.",
        "It pauses by itself when hidden, so a closed tab never keeps playing sound.",
        "Check VideoPlayer.is_available() when you must support minimal Linux images, which can lack PulseAudio."]),
]
