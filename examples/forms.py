"""A settings form with validation, selection controls, pickers and a confirmation dialog."""
from __future__ import annotations

import datetime as dt

from fluent_blue import (
    Button,
    Card,
    Container,
    DatePicker,
    FormField,
    Input,
    MessageDialog,
    PasswordInput,
    RadioGroup,
    Select,
    Stack,
    Switch,
    TextArea,
    ThemeManager,
)
from fluent_blue.compatibility.qt import QApplication, QWidget


def build() -> QWidget:
    window = Container(max_width=640)
    window.setWindowTitle("Account settings")
    card = Card(title="Account settings", subtitle="Fields validate when they lose focus.")

    email = FormField("Work email", Input(placeholder="name@company.com", prefix_icon="mail"), required=True,
                      validator=lambda value: None if "@" in value else "Enter a valid email address.")
    password = FormField("New password", PasswordInput(), helper="At least 8 characters.",
                         validator=lambda value: None if len(value) >= 8 else "Use at least 8 characters.")
    team = FormField("Team", Select(["Design", "Engineering", "Marketing"], placeholder="Choose a team"))
    start = FormField("Start date", DatePicker(date=dt.date.today()))
    density = FormField("Density", RadioGroup([("Comfortable", "comfortable"), ("Compact", "compact")], value="comfortable", orientation="horizontal"))
    notes = FormField("Notes", TextArea(placeholder="Anything your team should know", rows=3, max_length=280))
    updates = Switch("Email me product updates", checked=True)
    for field in (email, password, team, start, density, notes):
        card.add(field)
    card.add(updates)

    save = Button("Save changes", variant="primary", icon="check")

    def submit() -> None:
        valid = all(field.validate() for field in (email, password))
        if valid:
            MessageDialog.show_message(window, "Saved", "Your settings were updated.", variant="success")
        else:
            MessageDialog.show_message(window, "Check the form", "Some fields need attention.", variant="warning")

    save.clicked.connect(submit)
    card.add(Stack([save], direction="horizontal"))
    window.add(card)
    window.content_layout.addStretch(1)
    window.resize(720, 760)
    return window


def main() -> int:
    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    window = build()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
