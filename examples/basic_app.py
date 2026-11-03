"""The smallest useful Fluent Blue application: a card with an input, a button and a badge."""
from __future__ import annotations

from fluent_blue import Badge, Button, Card, Input, Text, ThemeManager, Toast
from fluent_blue.compatibility.qt import QApplication, QVBoxLayout, QWidget


def build() -> QWidget:
    window = QWidget()
    window.setWindowTitle("Fluent Blue")
    layout = QVBoxLayout(window)
    layout.setContentsMargins(32, 32, 32, 32)

    card = Card(title="Welcome", subtitle="A first look at the component library.")
    name = card.add(Input(placeholder="Enter your name...", prefix_icon="user"))
    start = card.add(Button("Get Started", variant="primary", size="large", icon="arrow-right", icon_position="right"))
    card.add(Badge("New", variant="success"))
    start.clicked.connect(lambda: Toast.show(f"Hello, {name.text() or 'there'}!", parent=window, variant="success"))

    layout.addWidget(card)
    layout.addWidget(Text("Switch themes at runtime with ThemeManager.toggle().", style="body-small", color="text-tertiary"))
    layout.addStretch(1)
    window.resize(480, 320)
    return window


def main() -> int:
    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    window = build()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
