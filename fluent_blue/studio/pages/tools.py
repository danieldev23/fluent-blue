"""Themes, Playground, About and Changelog pages."""
from __future__ import annotations

import traceback
from importlib import resources

from ... import (
    BINDING,
    BINDING_VERSION,
    QT_VERSION,
    Alert,
    Badge,
    Button,
    Card,
    CodeEditor,
    ColorPicker,
    Grid,
    PrimaryButton,
    ScrollArea,
    Select,
    Splitter,
    Stack,
    Text,
    ThemeManager,
    Toast,
    __version__,
    icon_names,
)
from ...compatibility.qt import QHBoxLayout, QTextBrowser, QVBoxLayout, QWidget
from ...core.palette import contrast_ratio
from .. import catalog
from .foundations import page
from .overview import ThemeTile


def themes_page() -> QWidget:
    shell, layout = page("Themes", "Switch themes at runtime, or build your own. Every open widget follows.")
    grid = Grid(min_column_width=220)
    for name in ThemeManager.themes():
        card = Card(title=ThemeManager.theme(name).label)
        tile = ThemeTile(name)
        tile.clicked.connect(ThemeManager.set_theme)
        card.add(tile)
        use = Button("Use theme", size="small")
        use.clicked.connect(lambda _=False, n=name: ThemeManager.set_theme(n))
        card.add(use)
        grid.add(card)
    layout.addWidget(grid)
    builder = Card(title="Custom theme", subtitle="Pick colors to preview them on the whole app. Setting primary regenerates the full ramp.")
    roles = {"primary": "#7C3AED", "background": "#F7F5FF", "surface": "#FFFFFF", "text_primary": "#1E1B4B"}
    pickers = {}
    row = QHBoxLayout()
    for role, value in roles.items():
        column = QVBoxLayout()
        column.addWidget(Text(role, style="label", color="text-secondary"))
        pickers[role] = ColorPicker(color=value)
        column.addWidget(pickers[role])
        row.addLayout(column)
    base = Select([("Light base", "light"), ("Dark base", "dark")], value="light")
    column = QVBoxLayout()
    column.addWidget(Text("base", style="label", color="text-secondary"))
    column.addWidget(base)
    row.addLayout(column)
    row.addStretch(1)
    builder.content_layout().addLayout(row)
    report = Badge("", variant="neutral")
    code = CodeEditor("", read_only=True, line_numbers=False)
    code.setFixedHeight(150)

    def current_code() -> str:
        lines = "".join(f'            "{r}": "{p.color()}",\n' for r, p in pickers.items())
        return ('ThemeManager.register_theme(\n    "custom",\n    {\n'
                f'        "base": "{base.value()}",\n        "colors": {{\n{lines}        }},\n    }},\n)\n'
                'ThemeManager.set_theme("custom")')

    def sync(*_args) -> None:
        code.set_code(current_code())
        ratio = contrast_ratio(pickers["text_primary"].color(), pickers["surface"].color())
        report.setText(f"Text contrast {ratio:.1f}:1 · {'AA pass' if ratio >= 4.5 else 'below AA'}")
        report.set_variant("success" if ratio >= 4.5 else "error")
        report.adjustSize()

    for picker in pickers.values():
        picker.color_changed.connect(sync)
    base.value_changed.connect(sync)
    sync()

    def apply() -> None:
        ThemeManager.register_theme("custom", {"base": base.value(), "colors": {r: p.color() for r, p in pickers.items()}, "label": "Custom"})
        ThemeManager.set_theme("custom")
        Toast.show("Custom theme applied", parent=builder, variant="success", duration=1500)

    apply_button = PrimaryButton("Apply custom theme", icon="wand")
    apply_button.clicked.connect(apply)
    reset = Button("Back to light")
    reset.clicked.connect(lambda: ThemeManager.set_theme("light"))
    builder.add(Stack([apply_button, reset, report], direction="horizontal", align="center"))
    builder.add(code)
    layout.addWidget(builder)
    layout.addStretch(1)
    return shell


class PlaygroundPage(QWidget):
    """Edit and run real code. The snippet must assign a widget to ``demo``."""

    def __init__(self) -> None:
        super().__init__()
        self._entries = {e.name: e for e in catalog.entries()}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 16)
        layout.setSpacing(12)
        layout.addWidget(Text("Playground", style="heading-1"))
        layout.addWidget(Text("Edit any example and run it. Assign your widget to demo. Ctrl+Enter also runs it.", style="body-large", color="text-secondary"))
        bar = QHBoxLayout()
        self.picker = Select(list(self._entries), value="DataTable")
        self.picker.setMinimumWidth(220)
        self.picker.value_changed.connect(self._load)
        run = PrimaryButton("Run", icon="play")
        run.setShortcut("Ctrl+Return")
        run.clicked.connect(self.run)
        bar.addWidget(self.picker)
        bar.addWidget(run)
        bar.addStretch(1)
        layout.addLayout(bar)
        self.editor = CodeEditor()
        self.stage = Card(tone="secondary")
        self.stage_layout = self.stage.content_layout()
        self.scroll = ScrollArea(self.stage, horizontal=True)
        self.split = Splitter([self.editor, self.scroll], sizes=[520, 620])
        layout.addWidget(self.split, 1)
        self.current = None
        self._load("DataTable")

    def _load(self, name: str) -> None:
        self.editor.set_code(self._entries[name].code.strip())
        self.run()

    def run(self) -> bool:
        """Execute the editor's code. Returns ``False`` and shows the traceback on failure."""
        scope: dict = {}
        try:
            exec(compile(self.editor.code(), "<playground>", "exec"), scope)  # noqa: S102 - the user's own code
            widget = scope["demo"]
            if not isinstance(widget, QWidget):
                raise TypeError("demo must be a QWidget.")
        except Exception:  # noqa: BLE001 - any error in user code is shown to the user
            error = traceback.format_exc(limit=2)
            widget = Alert("Your code raised an error", error, variant="error")
        ok = not isinstance(widget, Alert) or "demo" in scope
        self._show(widget)
        return ok

    def _show(self, widget) -> None:
        if self.current is not None:
            self.stage_layout.removeWidget(self.current)
            self.current.setParent(None)
            self.current.deleteLater()
        self.current = widget
        self.stage_layout.addWidget(widget)


def about_page() -> QWidget:
    shell, layout = page("About", "Fluent Blue is an open-source design system for Python desktop applications.")
    stats = Grid(columns=4)
    for title, value in (("Version", __version__), ("Catalog entries", str(len(catalog.entries()))), ("Icons", str(len(icon_names()))), ("Themes", str(len(ThemeManager.themes())))):
        card = Card()
        card.add(Text(title, style="label", color="text-secondary"))
        card.add(Text(value, style="heading-2"))
        stats.add(card)
    layout.addWidget(stats)
    runtime = Card(title="This runtime")
    runtime.add(Text(f"{BINDING} {BINDING_VERSION} on Qt {QT_VERSION}", color="text-secondary", selectable=True))
    layout.addWidget(runtime)
    notice = Card(title="License and independence")
    notice.add(Text("Released under the MIT License. The icons and artwork are original. Fluent Blue is an independent project, and it is not affiliated with or endorsed by Microsoft.", color="text-secondary", wrap=True))
    layout.addWidget(notice)
    layout.addStretch(1)
    return shell


def changelog_page() -> QWidget:
    shell = QWidget()
    layout = QVBoxLayout(shell)
    layout.setContentsMargins(24, 12, 24, 16)
    layout.addWidget(Text("Changelog", style="heading-1"))
    view = QTextBrowser()
    view.setMarkdown(resources.files("fluent_blue.studio").joinpath("CHANGELOG.md").read_text(encoding="utf-8"))
    view.setOpenExternalLinks(True)
    layout.addWidget(view, 1)
    return shell
