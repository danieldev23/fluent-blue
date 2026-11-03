"""Advanced components in tabs: code editor, wizard, pickers, tree and rich text."""
from __future__ import annotations

import datetime as dt

from fluent_blue import (
    Calendar,
    CodeEditor,
    ColorPicker,
    FilePicker,
    FormField,
    Input,
    Result,
    RichTextEditor,
    Stack,
    Tabs,
    Text,
    ThemeManager,
    TimePicker,
    TreeView,
    Wizard,
)
from fluent_blue.compatibility.qt import QApplication, QWidget

SAMPLE = '''from fluent_blue import ThemeManager

def toggle(window):
    """Switch theme at runtime."""
    print("Now using", ThemeManager.toggle())
'''


def build() -> QWidget:
    tabs = Tabs()
    tabs.setWindowTitle("Advanced components")

    editor = CodeEditor(SAMPLE, language="python")
    tabs.add_tab(editor, "Code editor", icon="code")

    wizard = Wizard(cancelable=True)
    name = Input(placeholder="Required")
    field = FormField("Project name", name, helper="Next is blocked until this has a value.")
    wizard.add_page("Details", field, lambda: bool(name.text()) or (field.set_error("Enter a project name.") or False))
    wizard.add_page("Review", Text("Check your details, then continue.", color="text-secondary"))
    wizard.add_page("Finish", Result("success", "All set", description="Your project is ready."))
    tabs.add_tab(wizard, "Wizard", icon="steps")

    pickers = Stack([
        FormField("Date", Calendar(selected=dt.date.today())),
        FormField("Time", TimePicker(time=dt.time(9, 30))),
        FormField("Accent color", ColorPicker()),
        FormField("Attachment", FilePicker(filter="Images (*.png *.jpg)")),
    ], spacing=4, padding=4, align="start")
    tabs.add_tab(pickers, "Pickers", icon="calendar")

    tree = TreeView([
        {"text": "Design system", "icon": "layers", "children": [
            {"text": "Foundations", "icon": "ruler", "children": [{"text": "Colors", "icon": "palette"}, {"text": "Type", "icon": "type"}]},
            {"text": "Components", "icon": "box"},
        ]},
        {"text": "Releases", "icon": "tag"},
    ])
    tabs.add_tab(tree, "Tree", icon="tree")

    tabs.add_tab(RichTextEditor(html="<p>Start writing <b>here</b>.</p>"), "Rich text", icon="edit")
    tabs.resize(960, 640)
    return tabs


def main() -> int:
    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    window = build()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
