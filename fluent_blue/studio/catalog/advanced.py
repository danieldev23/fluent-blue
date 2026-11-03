from . import Entry

G = "Advanced Components"
ENTRIES = [
    Entry("Calendar", G, '''
import datetime as dt

from fluent_blue import Calendar

demo = Calendar(selected=dt.date(2026, 11, 4), minimum=dt.date(2026, 1, 1))
''', ["Set minimum and maximum, so that invalid dates cannot be chosen at all."]),
    Entry("DatePicker", G, '''
import datetime as dt

from fluent_blue import DatePicker

demo = DatePicker(date=dt.date(2026, 11, 4), display_format="%d %b %Y")
''', ["Use a clear, unambiguous format, such as 04 Nov 2026."]),
    Entry("TimePicker", G, '''
import datetime as dt

from fluent_blue import TimePicker

demo = TimePicker(time=dt.time(9, 30), minute_step=15)
''', ["Match minute_step to how precise the task really is."]),
    Entry("ColorPicker", G, '''
from fluent_blue import ColorPicker

demo = ColorPicker(color="#1677FF")
''', ["Presets accept color roles, so they follow the active theme."]),
    Entry("FilePicker", G, '''
from fluent_blue import FilePicker, Stack

demo = Stack([FilePicker(filter="Images (*.png *.jpg)"), FilePicker(mode="directory", placeholder="No folder selected")])
''', ["Files can also be dropped onto the control."]),
    Entry("ImageViewer", G, '''
from fluent_blue import ImageViewer, ThemeManager
from fluent_blue.compatibility.qt import QLinearGradient, QPainter, QPixmap

picture = QPixmap(640, 360)
painter = QPainter(picture)
gradient = QLinearGradient(0, 0, 640, 360)
gradient.setColorAt(0, ThemeManager.qcolor("primary-800"))
gradient.setColorAt(1, ThemeManager.qcolor("primary-300"))
painter.fillRect(picture.rect(), gradient)
painter.end()
demo = ImageViewer(picture)
demo.setMinimumHeight(280)
''', ["The mouse wheel zooms under the cursor, and dragging pans the image."]),
    Entry("CodeEditor", G, '''
from fluent_blue import CodeEditor

demo = CodeEditor("""from fluent_blue import ThemeManager

def toggle(window):
    # Switch theme at runtime
    name = ThemeManager.toggle()
    print(f"Now using {name}", 42)
""", language="python")
demo.setMinimumHeight(170)
''', ["Tab inserts spaces, and Enter keeps the indentation level.", "Use read_only=True to display code."]),
    Entry("LogViewer", G, '''
from fluent_blue import LogViewer

demo = LogViewer()
demo.log("Starting worker pool", "debug")
demo.log("Connected to database", "info")
demo.log("Slow query: 1840 ms", "warning")
demo.log("Failed to write cache entry", "error")
demo.setMinimumHeight(200)
''', ["attach_logger routes Python logging here, safely from any thread."]),
    Entry("TreeView", G, '''
from fluent_blue import TreeView

demo = TreeView([
    {"text": "Design system", "icon": "layers", "children": [
        {"text": "Foundations", "icon": "ruler", "children": [{"text": "Colors", "icon": "palette"}, {"text": "Type", "icon": "type"}]},
        {"text": "Components", "icon": "box"},
    ]},
    {"text": "Releases", "icon": "tag"},
])
demo.setMinimumHeight(190)
''', ["set_filter keeps matching items along with their ancestors, so context is kept."]),
    Entry("FileTree", G, '''
from pathlib import Path

import fluent_blue
from fluent_blue import FileTree

demo = FileTree(str(Path(fluent_blue.__file__).parent), name_filters=["*.py"])
demo.setMinimumHeight(190)
''', ["Directories load lazily, so large folders stay fast."]),
    Entry("Stepper", G, '''
from fluent_blue import Stepper

demo = Stepper(["Account", "Workspace", "Billing", "Done"], current=2, clickable=True)
''', ["Keep to three to six steps with short titles."]),
    Entry("Wizard", G, '''
from fluent_blue import FormField, Input, Result, Text, Wizard

demo = Wizard()
name = Input(placeholder="Required")
field = FormField("Project name", name, helper="Next is blocked until this has a value.")

def check():
    field.set_error("" if name.text() else "Enter a project name.")
    return bool(name.text())

demo.add_page("Details", field, check)
demo.add_page("Review", Text("Check your details, then continue.", color="text-secondary"))
demo.add_page("Finish", Result("success", "All set", description="Your project is ready."))
demo.setMinimumHeight(330)
''', ["Validate on Next so that errors appear in context, on the step that caused them."]),
    Entry("RichTextEditor", G, '''
from fluent_blue import RichTextEditor

demo = RichTextEditor(html="<p>Start writing <b>here</b>. Use the toolbar or <i>keyboard shortcuts</i>.</p>")
demo.setMinimumHeight(180)
''', ["Store to_html or to_markdown, depending on what your backend needs."]),
]
