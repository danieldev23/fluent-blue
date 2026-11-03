"""CodeEditor, LogViewer and RichTextEditor."""
from __future__ import annotations

import datetime as dt
import logging
import re
from collections import deque

from ...compatibility.qt import (
    QFont, QFrame, QHBoxLayout, QInputDialog, QKeySequence, QPainter, QPlainTextEdit, QRect, QShortcut, QSize,
    QSyntaxHighlighter, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextEdit, QTextFormat, QTextListFormat,
    Qt, QVBoxLayout, QWidget, Signal,
)
from ...core.theme_manager import ThemeManager
from ..base import ThemedMixin, check_choice
from ..buttons.button import IconButton
from ..inputs.input import SearchInput
from ..selection.choice import MultiSelect
from ..selection.controls import Switch

_LANGUAGES: dict[str, list[tuple[str, str]]] = {
    "python": [
        (r"\b(?:False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|match|case)\b", "keyword"),
        (r"\b(?:self|cls)\b", "builtin"),
        (r"\b[0-9]+(?:\.[0-9]+)?\b", "number"),
        (r"\bdef\s+(\w+)|\bclass\s+(\w+)", "function"),
        (r"@\w+", "builtin"),
        (r"\"[^\"\n]*\"|'[^'\n]*'", "string"),
        (r"#[^\n]*", "comment"),
    ],
    "json": [
        (r"\b(?:true|false|null)\b", "keyword"),
        (r"-?\b[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b", "number"),
        (r"\"(?:[^\"\\\n]|\\.)*\"", "string"),
        (r"\"(?:[^\"\\\n]|\\.)*\"(?=\s*:)", "function"),
    ],
    "sql": [
        (r"(?i)\b(?:select|from|where|insert|into|values|update|set|delete|join|left|right|inner|outer|on|group|by|order|having|limit|as|and|or|not|null|create|table|primary|key)\b", "keyword"),
        (r"\b[0-9]+(?:\.[0-9]+)?\b", "number"),
        (r"'[^'\n]*'", "string"),
        (r"--[^\n]*", "comment"),
    ],
    "text": [],
}
_TOKEN_ROLES = {
    "keyword": "primary-text", "builtin": "info-text", "number": "warning-text",
    "function": "info-text", "string": "success-text", "comment": "text-tertiary",
}


class SyntaxHighlighter(QSyntaxHighlighter):
    """Regex-based highlighter whose colors come from theme roles."""

    def __init__(self, document, language: str = "python") -> None:
        super().__init__(document)
        self._rules: list[tuple[re.Pattern, str]] = []
        self._formats: dict[str, QTextCharFormat] = {}
        self.set_language(language)

    def set_language(self, language: str) -> None:
        check_choice("language", language, _LANGUAGES)
        self.language = language
        self._rules = [(re.compile(pattern), token) for pattern, token in _LANGUAGES[language]]
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the formats from the current theme and re-highlight."""
        self._formats = {}
        for token, role in _TOKEN_ROLES.items():
            char_format = QTextCharFormat()
            char_format.setForeground(ThemeManager.qcolor(role))
            if token == "keyword":
                char_format.setFontWeight(QFont.Weight.DemiBold)
            if token == "comment":
                char_format.setFontItalic(True)
            self._formats[token] = char_format
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # noqa: N802 - Qt override
        for pattern, token in self._rules:
            for match in pattern.finditer(text):
                group = next((i for i in range(1, (match.lastindex or 0) + 1) if match.group(i)), 0)
                start, end = match.span(group)
                self.setFormat(start, end - start, self._formats[token])
        if self.language == "python":
            self._multiline(text)

    def _multiline(self, text: str) -> None:
        delimiter = '"""'
        start = 0 if self.previousBlockState() == 1 else text.find(delimiter)
        self.setCurrentBlockState(0)
        while start >= 0:
            search_from = start + (0 if self.previousBlockState() == 1 and start == 0 else len(delimiter))
            end = text.find(delimiter, search_from)
            if end < 0:
                self.setCurrentBlockState(1)
                self.setFormat(start, len(text) - start, self._formats["string"])
                return
            length = end - start + len(delimiter)
            self.setFormat(start, length, self._formats["string"])
            start = text.find(delimiter, start + length)


class _LineNumbers(QWidget):
    def __init__(self, editor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(self.editor.gutter_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        self.editor.paint_gutter(event)


class CodeEditor(ThemedMixin, QPlainTextEdit):
    """A code editor with line numbers, syntax colors and smart indentation.

    Args:
        text: Initial content.
        language: ``python``, ``json``, ``sql`` or ``text``.
        read_only: Disable editing.
        line_numbers: Show the gutter.
        tab_width: Spaces per indent level.

    Signals:
        code_changed(str): The content changed.
    """

    code_changed = Signal(str)

    def __init__(self, text: str = "", parent=None, *, language: str = "python", read_only: bool = False,
                 line_numbers: bool = True, tab_width: int = 4) -> None:
        super().__init__(parent)
        self._tab = " " * tab_width
        self._show_numbers = line_numbers
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setFont(ThemeManager.font("monospace"))
        self.setAccessibleName("Code editor")
        self.gutter = _LineNumbers(self)
        self.highlighter = SyntaxHighlighter(self.document(), language)
        self.blockCountChanged.connect(self._update_gutter_width)
        self.updateRequest.connect(self._update_gutter)
        self.cursorPositionChanged.connect(self._highlight_line)
        self.textChanged.connect(lambda: self.code_changed.emit(self.toPlainText()))
        self.bind_theme()
        self.setPlainText(text)
        self.setReadOnly(read_only)
        self._update_gutter_width()
        self._highlight_line()

    def code(self) -> str:
        return self.toPlainText()

    def set_code(self, text: str) -> None:
        self.setPlainText(text)

    def set_language(self, language: str) -> None:
        self.highlighter.set_language(language)

    def refresh_theme(self) -> None:
        self.highlighter.refresh()
        self._highlight_line()
        self.gutter.update()

    def gutter_width(self) -> int:
        if not self._show_numbers:
            return 0
        digits = max(2, len(str(self.blockCount())))
        return 20 + self.fontMetrics().horizontalAdvance("9") * digits

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        rect = self.contentsRect()
        self.gutter.setGeometry(QRect(rect.left(), rect.top(), self.gutter_width(), rect.height()))

    def paint_gutter(self, event) -> None:
        painter = QPainter(self.gutter)
        painter.setFont(self.font())
        block = self.firstVisibleBlock()
        number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        current = self.textCursor().blockNumber()
        while block.isValid() and top <= event.rect().bottom():
            height = round(self.blockBoundingRect(block).height())
            if block.isVisible() and top + height >= event.rect().top():
                painter.setPen(ThemeManager.qcolor("text-primary" if number == current else "text-tertiary"))
                painter.drawText(0, top, self.gutter.width() - 10, height,
                                 int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter), str(number + 1))
            block = block.next()
            top += height
            number += 1
        painter.end()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        key = event.key()
        cursor = self.textCursor()
        if key == Qt.Key.Key_Tab and not event.modifiers():
            cursor.insertText(self._tab)
        elif key == Qt.Key.Key_Backtab:
            self._dedent(cursor)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            line = cursor.block().text()[:cursor.positionInBlock()]
            indent = line[:len(line) - len(line.lstrip())]
            if line.rstrip().endswith((":", "{", "[", "(")):
                indent += self._tab
            cursor.insertText("\n" + indent)
        else:
            super().keyPressEvent(event)

    def _dedent(self, cursor) -> None:
        text = cursor.block().text()
        count = min(len(self._tab), len(text) - len(text.lstrip(" ")))
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        for _ in range(count):
            cursor.deleteChar()

    def _update_gutter_width(self, _count: int = 0) -> None:
        self.setViewportMargins(self.gutter_width(), 0, 0, 0)

    def _update_gutter(self, rect, dy: int) -> None:
        if dy:
            self.gutter.scroll(0, dy)
        else:
            self.gutter.update(0, rect.y(), self.gutter.width(), rect.height())

    def _highlight_line(self) -> None:
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(ThemeManager.qcolor("surface-tertiary"))
        selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])
        self.gutter.update()


class _LogHandler(logging.Handler):
    _LEVELS = {logging.DEBUG: "debug", logging.INFO: "info", logging.WARNING: "warning", logging.ERROR: "error", logging.CRITICAL: "error"}

    def __init__(self, viewer) -> None:
        super().__init__()
        self.viewer = viewer

    def emit(self, record) -> None:
        # A queued signal makes this safe to call from worker threads.
        self.viewer.record_received.emit(self.format(record), self._LEVELS.get(record.levelno, "info"))


LOG_LEVELS = ("debug", "info", "warning", "error")


class LogViewer(ThemedMixin, QFrame):
    """A live log view with level filtering, search and tailing.

    Args:
        max_entries: Retained entries; the oldest are dropped first.
        timestamps: Prefix each entry with its time.

    Signals:
        entry_added(str, str): The message and level of a new entry.
    """

    entry_added = Signal(str, str)
    record_received = Signal(str, str)
    _ROLES = {"debug": "text-tertiary", "info": "text-primary", "warning": "warning-text", "error": "error-text"}

    def __init__(self, parent=None, *, max_entries: int = 10000, timestamps: bool = True) -> None:
        super().__init__(parent)
        self._entries: deque = deque(maxlen=max_entries)
        self._timestamps = timestamps
        self._levels = set(LOG_LEVELS)
        self._query = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        bar = QHBoxLayout()
        bar.setContentsMargins(8, 8, 8, 8)
        bar.setSpacing(8)
        self.search = SearchInput(size="small", placeholder="Filter logs…")
        self.search.search_changed.connect(self.set_query)
        self.level_select = MultiSelect([(n.title(), n) for n in LOG_LEVELS], values=list(LOG_LEVELS), placeholder="Levels", max_labels=1)
        self.level_select.values_changed.connect(self.set_levels)
        self.tail = Switch("Tail", checked=True)
        clear = IconButton("trash", size="small", tooltip="Clear log")
        clear.clicked.connect(self.clear)
        bar.addWidget(self.search, 1)
        bar.addWidget(self.level_select)
        bar.addWidget(self.tail)
        bar.addWidget(clear)
        layout.addLayout(bar)
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.text.setMaximumBlockCount(max_entries)
        self.text.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.text.setFont(ThemeManager.font("monospace"))
        self.text.setAccessibleName("Log output")
        layout.addWidget(self.text, 1)
        self.record_received.connect(self.log)
        self.bind_theme()

    def log(self, message: str, level: str = "info") -> None:
        """Append an entry. ``level`` is ``debug``, ``info``, ``warning`` or ``error``."""
        check_choice("level", level, LOG_LEVELS)
        stamp = dt.datetime.now().strftime("%H:%M:%S") if self._timestamps else ""
        entry = (stamp, level, message)
        self._entries.append(entry)
        if self._visible(entry):
            self._write(entry)
        self.entry_added.emit(message, level)

    def entries(self) -> list[tuple[str, str, str]]:
        """All retained entries as ``(time, level, message)``."""
        return list(self._entries)

    def visible_text(self) -> str:
        return self.text.toPlainText()

    def clear(self) -> None:
        self._entries.clear()
        self.text.clear()

    def set_levels(self, levels) -> None:
        """Show only these levels."""
        self._levels = set(levels)
        self._render()

    def set_query(self, query: str) -> None:
        """Show only entries containing this text."""
        self._query = query.lower()
        self._render()

    def attach_logger(self, logger: logging.Logger | None = None, level: int = logging.DEBUG) -> logging.Handler:
        """Route a ``logging`` logger here, thread-safely. Returns the handler to remove later."""
        handler = _LogHandler(self)
        handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))
        handler.setLevel(level)
        (logger or logging.getLogger()).addHandler(handler)
        return handler

    def export(self, path) -> int:
        """Write visible entries to a text file and return the count."""
        rows = [e for e in self._entries if self._visible(e)]
        with open(path, "w", encoding="utf-8") as handle:
            for stamp, level, message in rows:
                handle.write(f"{stamp} {level.upper():<8}{message}\n")
        return len(rows)

    def refresh_theme(self) -> None:
        self._render()

    def _visible(self, entry) -> bool:
        return entry[1] in self._levels and (not self._query or self._query in entry[2].lower())

    def _write(self, entry) -> None:
        stamp, level, message = entry
        cursor = QTextCursor(self.text.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if not self.text.document().isEmpty():
            cursor.insertBlock()
        char_format = QTextCharFormat()
        char_format.setForeground(ThemeManager.qcolor("text-tertiary"))
        cursor.insertText(f"{stamp} {level.upper():<8}" if stamp else f"{level.upper():<8}", char_format)
        char_format.setForeground(ThemeManager.qcolor(self._ROLES[level]))
        cursor.insertText(message, char_format)
        if self.tail.isChecked():
            bar = self.text.verticalScrollBar()
            bar.setValue(bar.maximum())

    def _render(self) -> None:
        self.text.clear()
        for entry in self._entries:
            if self._visible(entry):
                self._write(entry)


class RichTextArea(QTextEdit):
    """The editing surface of :class:`RichTextEditor`."""


class RichTextEditor(ThemedMixin, QFrame):
    """A rich text editor with a formatting toolbar.

    Args:
        html: Initial HTML content.
        placeholder: Placeholder text.
        read_only: Hide the toolbar and disable editing.

    Signals:
        content_changed: The document changed.
    """

    content_changed = Signal()

    def __init__(self, parent=None, *, html: str = "", placeholder: str = "Write something…", read_only: bool = False) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.toolbar = QHBoxLayout()
        self.toolbar.setContentsMargins(6, 6, 6, 6)
        self.toolbar.setSpacing(2)
        layout.addLayout(self.toolbar)
        self.editor = RichTextArea()
        self.editor.setPlaceholderText(placeholder)
        self.editor.setAccessibleName("Rich text")
        self.editor.setTabChangesFocus(True)
        layout.addWidget(self.editor, 1)
        self.buttons: dict[str, IconButton] = {}
        self._add_toggle("bold", "Bold (Ctrl+B)", "Ctrl+B", self.toggle_bold)
        self._add_toggle("italic", "Italic (Ctrl+I)", "Ctrl+I", self.toggle_italic)
        self._add_toggle("underline", "Underline (Ctrl+U)", "Ctrl+U", self.toggle_underline)
        self._add_toggle("strikethrough", "Strikethrough", None, self.toggle_strike)
        self.toolbar.addSpacing(8)
        self._add_button("list", "Bullet list", lambda: self.toggle_list(QTextListFormat.Style.ListDisc))
        self._add_button("list-ordered", "Numbered list", lambda: self.toggle_list(QTextListFormat.Style.ListDecimal))
        self.toolbar.addSpacing(8)
        for name, tip, flag in (("align-left", "Align left", Qt.AlignmentFlag.AlignLeft),
                                ("align-center", "Align center", Qt.AlignmentFlag.AlignCenter),
                                ("align-right", "Align right", Qt.AlignmentFlag.AlignRight)):
            self._add_button(name, tip, lambda _=False, f=flag: self.editor.setAlignment(f))
        self.toolbar.addSpacing(8)
        self._add_button("link", "Insert link", self._prompt_link)
        self._add_button("eraser", "Clear formatting", self.clear_formatting)
        self.toolbar.addStretch(1)
        self.editor.currentCharFormatChanged.connect(lambda _f: self._sync_toggles())
        self.editor.cursorPositionChanged.connect(self._sync_toggles)
        self.editor.textChanged.connect(lambda: self.content_changed.emit())
        self.bind_theme()
        if html:
            self.editor.setHtml(html)
        if read_only:
            self.editor.setReadOnly(True)
            for button in self.buttons.values():
                button.hide()

    # ---- content ---------------------------------------------------------------------
    def to_html(self) -> str:
        return self.editor.toHtml()

    def to_markdown(self) -> str:
        return self.editor.toMarkdown()

    def to_plain_text(self) -> str:
        return self.editor.toPlainText()

    def set_html(self, html: str) -> None:
        self.editor.setHtml(html)

    def set_markdown(self, text: str) -> None:
        self.editor.setMarkdown(text)

    # ---- formatting ---------------------------------------------------------------------
    def toggle_bold(self) -> None:
        bold = self.editor.fontWeight() > QFont.Weight.Normal.value
        self._merge(lambda f: f.setFontWeight(QFont.Weight.Normal if bold else QFont.Weight.Bold))

    def toggle_italic(self) -> None:
        on = not self.editor.fontItalic()
        self._merge(lambda f: f.setFontItalic(on))

    def toggle_underline(self) -> None:
        on = not self.editor.fontUnderline()
        self._merge(lambda f: f.setFontUnderline(on))

    def toggle_strike(self) -> None:
        on = not self.editor.currentCharFormat().fontStrikeOut()
        self._merge(lambda f: f.setFontStrikeOut(on))

    def toggle_list(self, style) -> None:
        """Turn the current blocks into a list, or remove them from the current list."""
        cursor = self.editor.textCursor()
        current = cursor.currentList()
        if current is not None:
            block_format = QTextBlockFormat()
            current.remove(cursor.block())
            block_format.setIndent(0)
            cursor.setBlockFormat(block_format)
        else:
            cursor.createList(style)

    def insert_link(self, url: str, text: str | None = None) -> None:
        """Insert a link at the cursor, using the selection as the label if there is one."""
        cursor = self.editor.textCursor()
        label = text or cursor.selectedText() or url
        char_format = QTextCharFormat()
        char_format.setAnchor(True)
        char_format.setAnchorHref(url)
        char_format.setForeground(ThemeManager.qcolor("primary-text"))
        char_format.setFontUnderline(True)
        cursor.insertText(label, char_format)
        self.editor.setCurrentCharFormat(QTextCharFormat())

    def clear_formatting(self) -> None:
        """Remove character formatting from the selection."""
        cursor = self.editor.textCursor()
        cursor.setCharFormat(QTextCharFormat())
        self.editor.setCurrentCharFormat(QTextCharFormat())

    def refresh_theme(self) -> None:
        palette = self.editor.palette()
        palette.setColor(palette.ColorRole.Text, ThemeManager.qcolor("text-primary"))
        palette.setColor(palette.ColorRole.PlaceholderText, ThemeManager.qcolor("text-tertiary"))
        self.editor.setPalette(palette)

    # ---- internals -----------------------------------------------------------------------
    def _add_button(self, icon: str, tip: str, handler) -> IconButton:
        button = IconButton(icon, size="small", tooltip=tip)
        button.clicked.connect(handler)
        self.toolbar.addWidget(button)
        self.buttons[icon] = button
        return button

    def _add_toggle(self, icon: str, tip: str, shortcut: str | None, handler) -> None:
        button = self._add_button(icon, tip, lambda _=False: handler())
        button.setCheckable(True)
        if shortcut:
            QShortcut(QKeySequence(shortcut), self.editor, activated=handler)

    def _merge(self, change) -> None:
        char_format = QTextCharFormat()
        change(char_format)
        cursor = self.editor.textCursor()
        cursor.mergeCharFormat(char_format)
        self.editor.mergeCurrentCharFormat(char_format)
        self._sync_toggles()
        self.editor.setFocus()

    def _sync_toggles(self) -> None:
        current = self.editor.currentCharFormat()
        self.buttons["bold"].setChecked(self.editor.fontWeight() > QFont.Weight.Normal.value)
        self.buttons["italic"].setChecked(self.editor.fontItalic())
        self.buttons["underline"].setChecked(self.editor.fontUnderline())
        self.buttons["strikethrough"].setChecked(current.fontStrikeOut())

    def _prompt_link(self) -> None:
        url, accepted = QInputDialog.getText(self, "Insert link", "URL:")
        if accepted and url:
            self.insert_link(url)

