"""Keyboard-first command launcher."""
from __future__ import annotations

from dataclasses import dataclass, field

from ...compatibility.qt import (
    QDialog,
    QEvent,
    QFrame,
    QKeySequence,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QShortcut,
    QSize,
    Qt,
    QVBoxLayout,
    Signal,
)
from ...core.animations import apply_elevation
from ...icons import icon as make_icon
from ..base import ThemedMixin

_ID_ROLE = Qt.ItemDataRole.UserRole


@dataclass
class Command:
    """An entry in the palette. ``action`` runs when the command is chosen."""

    id: str
    title: str
    subtitle: str = ""
    icon: str | None = None
    keywords: str = ""
    action: object = field(default=None, repr=False)


def fuzzy_score(query: str, text: str) -> int | None:
    """Score a subsequence match; higher is better and ``None`` means no match."""
    query, text = query.lower(), text.lower()
    if not query:
        return 0
    if query in text:
        return 1000 - text.index(query) - len(text)
    position, score = -1, 0
    for char in query:
        found = text.find(char, position + 1)
        if found < 0:
            return None
        score -= found - position
        position = found
    return score


class CommandPalette(ThemedMixin, QDialog):
    """A searchable command launcher.

    Args:
        parent: Window the palette opens over and listens on for the shortcut.
        commands: Initial :class:`Command` objects.
        shortcut: Global shortcut, or ``None`` for none.
        placeholder: Search placeholder.

    Signals:
        command_triggered(str): The id of the chosen command.
    """

    command_triggered = Signal(str)

    def __init__(self, parent=None, *, commands=None, shortcut: str | None = "Ctrl+K",
                 placeholder: str = "Type a command or search…") -> None:
        super().__init__(parent)
        self._commands: list[Command] = list(commands or [])
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAccessibleName("Command palette")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 16, 24, 32)
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        outer.addWidget(self.panel)
        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.search = QLineEdit()
        self.search.setPlaceholderText(placeholder)
        self.search.setAccessibleName("Search commands")
        self.search.textChanged.connect(self._refilter)
        self.search.installEventFilter(self)
        layout.addWidget(self.search)
        self.list = QListWidget()
        self.list.setIconSize(QSize(16, 16))
        self.list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.list.setUniformItemSizes(True)
        self.list.itemActivated.connect(self._activate)
        self.list.itemClicked.connect(self._activate)
        layout.addWidget(self.list, 1)
        self.hint = QLabel("↑↓ navigate   ↵ run   esc close")
        self.hint.setObjectName("hint")
        layout.addWidget(self.hint)
        self.resize(640, 440)
        self.bind_theme()
        apply_elevation(self.panel, 4)
        if shortcut and parent is not None:
            self._shortcut = QShortcut(QKeySequence(shortcut), parent)
            self._shortcut.activated.connect(self.open_palette)
        self._refilter("")

    def add_command(self, command: Command) -> None:
        """Add a command."""
        self._commands.append(command)
        self._refilter(self.search.text())

    def set_commands(self, commands) -> None:
        """Replace all commands."""
        self._commands = list(commands)
        self._refilter(self.search.text())

    def visible_ids(self) -> list[str]:
        """Ids currently listed, in display order."""
        return [self.list.item(i).data(_ID_ROLE) for i in range(self.list.count())]

    def open_palette(self) -> None:
        """Show the palette centered near the top of its parent window."""
        self.search.clear()
        self._refilter("")
        anchor = self.parentWidget().window() if self.parentWidget() else None
        if anchor is not None:
            top_left = anchor.mapToGlobal(anchor.rect().topLeft())
            self.move(top_left.x() + (anchor.width() - self.width()) // 2, top_left.y() + 48)
        self.show()
        self.raise_()
        self.search.setFocus()

    def run(self, command_id: str) -> None:
        """Run a command by id."""
        command = next(c for c in self._commands if c.id == command_id)
        self.hide()
        if callable(command.action):
            command.action()
        self.command_triggered.emit(command_id)

    def refresh_theme(self) -> None:
        apply_elevation(self.panel, 4)
        self._refilter(self.search.text())

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if watched is self.search and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Down, Qt.Key.Key_Up):
                step = 1 if key == Qt.Key.Key_Down else -1
                count = self.list.count()
                if count:
                    self.list.setCurrentRow((self.list.currentRow() + step) % count)
                return True
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                current = self.list.currentItem()
                if current:
                    self._activate(current)
                return True
            if key == Qt.Key.Key_Escape:
                self.hide()
                return True
        return super().eventFilter(watched, event)

    def _refilter(self, query: str) -> None:
        scored = []
        for order, command in enumerate(self._commands):
            score = fuzzy_score(query, f"{command.title} {command.subtitle} {command.keywords}")
            if score is not None:
                scored.append((-score, order, command))
        scored.sort(key=lambda entry: entry[:2])
        self.list.clear()
        for _, _, command in scored:
            text = f"{command.title}   —   {command.subtitle}" if command.subtitle else command.title
            item = QListWidgetItem(make_icon(command.icon, 16, "text-secondary") if command.icon else make_icon("zap", 16), text)
            item.setData(_ID_ROLE, command.id)
            self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)

    def _activate(self, item) -> None:
        self.run(item.data(_ID_ROLE))
