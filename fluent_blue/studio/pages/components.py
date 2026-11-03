"""A page per component group, generated from the catalog. Every preview is the live widget."""
from __future__ import annotations

from ... import Badge, Button, Card, CodeEditor, Column, DataTable, IconButton, ScrollArea, Tabs, Text, Toast
from ...compatibility.qt import QApplication, QHBoxLayout, QSizePolicy, Qt, QTimer, QVBoxLayout, QWidget
from ...agent_prompts import component_prompt
from .. import catalog, introspect

_NATIVE_SIGNALS = ("clicked", "toggled", "valueChanged", "textChanged", "returnPressed", "currentChanged")
_DESCRIPTIONS = {
    "Buttons": "Actions, from the single primary path to quiet toolbar controls.",
    "Inputs": "Collect text and numbers, with validation built in.",
    "Selection": "Choose from options with the control that suits the choice.",
    "Navigation": "Move around an application and find commands quickly.",
    "Data Display": "Present content, status and progress.",
    "Data Tables": "A model/view table for real data: sort, filter, page, select and export.",
    "Feedback": "Tell people what happened, and what is happening now.",
    "Layout": "Structure pages with token-based spacing, and overlay panels.",
    "Advanced Components": "Pickers, editors, viewers, trees and multi-step flows.",
}


def api_table(rows, columns, height_rows: int | None = None) -> DataTable:
    table = DataTable(columns, rows, page_size=None, selection="none", searchable=False, column_menu=False, exportable=False, row_height=32)
    table.setMinimumHeight(36 + 32 * (height_rows or len(rows)) + 6)
    table.setMaximumHeight(table.minimumHeight())
    return table


class ComponentSection(Card):
    """Live preview, event readout, code, properties, signals and usage for one component."""

    def __init__(self, entry: catalog.Entry) -> None:
        super().__init__()
        self.entry = entry
        layout = self.content_layout()
        layout.setSpacing(10)
        head = QHBoxLayout()
        head.setSpacing(8)
        head.addWidget(Text(entry.name, style="heading-3"))
        head.addWidget(Badge(entry.group, variant="primary"))
        head.addStretch(1)
        layout.addLayout(head)
        layout.addWidget(Text(introspect.summary(entry.cls), color="text-secondary", wrap=True))
        stage = Card(tone="secondary")
        stage_layout = stage.content_layout()
        stage_layout.setSpacing(10)
        self.demo = entry.run()
        stage_layout.addWidget(self.demo)
        self.event_label = Text("Interact with the preview to see its signals here.", style="caption", color="text-tertiary")
        stage_layout.addWidget(self.event_label)
        layout.addWidget(stage)
        self._wire_events()
        tabs = Tabs()
        builders = ((self._code_tab, "Python", "code"), (self._property_tab, "Properties", "sliders"),
                    (self._signal_tab, "Signals", "zap"), (self._usage_tab, "Usage", "info-circle"), (self._agent_tab, "AI Prompt", "wand"))
        holders, contents = [], {}
        for _build, title, icon in builders:
            holder = QWidget()
            holder_layout = QVBoxLayout(holder)
            holder_layout.setContentsMargins(0, 0, 0, 0)
            holders.append(holder)
            tabs.add_tab(holder, title, icon=icon)

        def build_tab(current: int) -> None:
            # Tabs build on first visit, and hidden content has no size, so the tabs
            # take the height of the visible page and the page opens quickly.
            if current not in contents:
                contents[current] = builders[current][0]()
                holders[current].layout().addWidget(contents[current])
            for index, content in contents.items():
                content.setVisible(index == current)

        tabs.currentChanged.connect(build_tab)
        build_tab(0)
        tabs.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        layout.addWidget(tabs)

    def _code_tab(self) -> QWidget:
        code = self.entry.code.strip()
        holder = QWidget()
        column = QVBoxLayout(holder)
        column.setContentsMargins(0, 8, 0, 0)
        editor = CodeEditor(code, read_only=True)
        editor.setFixedHeight(min(320, 18 * (code.count("\n") + 1) + 16))
        copy = IconButton("copy", size="small", tooltip="Copy code", variant="secondary")

        def do_copy() -> None:
            QApplication.clipboard().setText(code)
            Toast.show("Code copied", parent=self, variant="success", duration=1500)

        copy.clicked.connect(do_copy)
        bar = QHBoxLayout()
        bar.addStretch(1)
        bar.addWidget(copy)
        column.addLayout(bar)
        column.addWidget(editor)
        column.addStretch(1)
        return holder

    def _property_tab(self) -> QWidget:
        rows = [{"name": p.name, "default": p.default, "description": p.description} for p in introspect.properties(self.entry.cls)]
        if not rows:
            return Text("This component has no constructor options.", color="text-tertiary")
        return api_table(rows, [Column("name", width=150), Column("default", width=170), Column("description")])

    def _signal_tab(self) -> QWidget:
        rows = [{"signal": s.name, "arguments": s.args, "description": s.description} for s in introspect.signals(self.entry.cls)]
        note = introspect.inherited_signals_note(self.entry.cls)
        holder = QWidget()
        column = QVBoxLayout(holder)
        column.setContentsMargins(0, 8, 0, 0)
        if rows:
            column.addWidget(api_table(rows, [Column("signal", width=170), Column("arguments", width=130), Column("description")]))
        if note or not rows:
            column.addWidget(Text(note or "This component adds no signals of its own.", color="text-secondary", wrap=True))
        column.addStretch(1)
        return holder

    def _usage_tab(self) -> QWidget:
        holder = QWidget()
        column = QVBoxLayout(holder)
        column.setContentsMargins(0, 8, 0, 0)
        for tip in self.entry.tips:
            column.addWidget(Text(f"•  {tip}", color="text-secondary", wrap=True))
        column.addStretch(1)
        return holder

    def _agent_tab(self) -> QWidget:
        brief = component_prompt(self.entry.name)
        holder = QWidget()
        column = QVBoxLayout(holder)
        column.setContentsMargins(0, 8, 0, 0)
        bar = QHBoxLayout()
        bar.addWidget(Text("Paste this into any AI coding agent. It is generated from the source, so it matches this version.", style="body-small", color="text-secondary", wrap=True), 1)
        copy = Button("Copy prompt", size="small", icon="copy", variant="primary")

        def do_copy() -> None:
            QApplication.clipboard().setText(brief)
            Toast.show(f"{self.entry.name} prompt copied", parent=self, variant="success", duration=1500)

        copy.clicked.connect(do_copy)
        bar.addWidget(copy)
        column.addLayout(bar)
        view = CodeEditor(brief, language="text", read_only=True, line_numbers=False)
        view.setFixedHeight(320)
        column.addWidget(view)
        column.addStretch(1)
        return holder

    def _wire_events(self) -> None:
        for widget in [self.demo, *self.demo.findChildren(QWidget)]:
            if not type(widget).__module__.startswith("fluent_blue.components"):
                continue
            names = set(introspect.declared_signal_names(widget))
            names.update(n for n in _NATIVE_SIGNALS if hasattr(widget, n) and not widget.objectName().startswith("qt_"))
            label = type(widget).__name__
            for name in names:
                signal = getattr(widget, name, None)
                if hasattr(signal, "connect"):
                    signal.connect(lambda *args, n=name, w=label: self._show_event(w, n, args))

    def _show_event(self, widget: str, name: str, args) -> None:
        text = ", ".join(repr(a)[:40] for a in args if not isinstance(a, bool) or name == "toggled")
        self.event_label.setText(f"{widget}.{name}({text})")
        self.event_label.set_color("primary-text")


class ComponentGroupPage(QWidget):
    """All components of a group. The sections build on first visit, keeping startup quick."""

    def __init__(self, group: str) -> None:
        super().__init__()
        self.group = group
        self.sections: dict[str, ComponentSection] = {}
        content = QWidget()
        self._layout = QVBoxLayout(content)
        self._layout.setContentsMargins(24, 12, 24, 32)
        self._layout.setSpacing(16)
        self._layout.addWidget(Text(group, style="heading-1"))
        self._layout.addWidget(Text(_DESCRIPTIONS.get(group, ""), style="body-large", color="text-secondary", wrap=True))
        self._layout.addStretch(1)
        self._pending = list(catalog.by_group(group))
        self.scroll = ScrollArea(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.scroll)
        # Build the first section now, the rest between events, so the page appears at once
        # and stays responsive while it fills.
        self._builder = QTimer(self)
        self._builder.setInterval(0)
        self._builder.timeout.connect(self._build_next)
        self._build_next()
        self._builder.start()

    def _build_next(self) -> None:
        if not self._pending:
            self._builder.stop()
            return
        entry = self._pending.pop(0)
        section = ComponentSection(entry)
        self.sections[entry.name] = section
        self._layout.insertWidget(self._layout.count() - 1, section)

    def ensure_built(self, name: str | None = None) -> None:
        """Build pending sections now, up to and including ``name``, or all of them."""
        while self._pending and (name is None or name not in self.sections):
            self._build_next()

    def reveal(self, name: str) -> None:
        """Scroll to a component's section."""
        self.ensure_built(name)
        QApplication.processEvents()
        section = self.sections.get(name)
        if section:
            self.scroll.ensureWidgetVisible(section, 0, 16)
            self.scroll.verticalScrollBar().setValue(section.y() - 12)
