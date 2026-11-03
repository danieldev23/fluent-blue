"""Interactive colored terminal and log viewer widget for tools, bots, and debug consoles."""
from __future__ import annotations

import re
import time
from ...compatibility.qt import (
    QAction,
    QColor,
    QHBoxLayout,
    QPlainTextEdit,
    QSize,
    QTextCharFormat,
    QTextCursor,
    QToolButton,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ..base import ThemedMixin, apply_common, set_style_prop


class ConsoleWidget(ThemedMixin, QWidget):
    """A high-performance rich console / terminal widget for desktop tools and logging.

    Features:
    - Automatic tag coloring for logs: ``[+]`` (success), ``[-]`` (error), ``[*]`` (info), ``[!]`` (warning)
    - Auto-scroll lock / unlock toggle
    - Clear, Copy All, and Pause controls
    - Monospace typography aligned with design tokens

    Args:
        max_lines: Max number of log lines to retain in memory (default 2000).
        show_toolbar: Whether to render the quick action toolbar on top.
        disabled: Start disabled.
    """

    line_appended = Signal(str)

    def __init__(
        self,
        parent=None,
        *,
        max_lines: int = 2000,
        show_toolbar: bool = True,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.bind_theme()
        self._auto_scroll = True
        self._max_lines = max_lines

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if show_toolbar:
            toolbar = QHBoxLayout()
            toolbar.setContentsMargins(4, 2, 4, 2)
            toolbar.setSpacing(6)

            self._btn_clear = QToolButton(self)
            self._btn_clear.setIcon(make_icon("trash", 14, "text-secondary"))
            self._btn_clear.setToolTip("Clear console")
            self._btn_clear.clicked.connect(self.clear)
            toolbar.addWidget(self._btn_clear)

            self._btn_copy = QToolButton(self)
            self._btn_copy.setIcon(make_icon("copy", 14, "text-secondary"))
            self._btn_copy.setToolTip("Copy all logs")
            self._btn_copy.clicked.connect(self.copy_all)
            toolbar.addWidget(self._btn_copy)

            self._btn_scroll = QToolButton(self)
            self._btn_scroll.setIcon(make_icon("arrow-down", 14, "primary"))
            self._btn_scroll.setToolTip("Toggle auto-scroll")
            self._btn_scroll.setCheckable(True)
            self._btn_scroll.setChecked(True)
            self._btn_scroll.clicked.connect(self._toggle_scroll)
            toolbar.addWidget(self._btn_scroll)

            toolbar.addStretch()
            layout.addLayout(toolbar)

        self._text_edit = QPlainTextEdit(self)
        self._text_edit.setReadOnly(True)
        self._text_edit.setMaximumBlockCount(max_lines)
        self._text_edit.setFont(ThemeManager.font("monospace"))
        layout.addWidget(self._text_edit)

        set_style_prop(self, "fbComponent", "consoleWidget")
        apply_common(self, disabled=disabled, tooltip=tooltip)

    def _toggle_scroll(self, checked: bool) -> None:
        self._auto_scroll = checked

    def log(self, text: str, tag: str | None = None) -> None:
        """Append a log line with optional timestamp and tag parsing."""
        ts = time.strftime("[%H:%M:%S] ")
        full_line = f"{ts}{tag + ' ' if tag else ''}{text}"

        cursor = self._text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Detect tag styling
        fmt = QTextCharFormat()
        clean = full_line.strip()

        if "[+]" in clean or "SUCCESS" in clean:
            fmt.setForeground(ThemeManager.qcolor("success"))
        elif "[-]" in clean or "ERROR" in clean or "FAILED" in clean:
            fmt.setForeground(ThemeManager.qcolor("error"))
        elif "[!]" in clean or "WARN" in clean:
            fmt.setForeground(ThemeManager.qcolor("warning"))
        elif "[*]" in clean or "INFO" in clean:
            fmt.setForeground(ThemeManager.qcolor("info"))
        else:
            fmt.setForeground(ThemeManager.qcolor("text-primary"))

        cursor.insertText(full_line + "\n", fmt)

        if self._auto_scroll:
            self._text_edit.setTextCursor(cursor)
            self._text_edit.ensureCursorVisible()

        self.line_appended.emit(full_line)

    def clear(self) -> None:
        """Clear all text in console."""
        self._text_edit.clear()

    def copy_all(self) -> None:
        """Copy all log content to system clipboard."""
        from ...compatibility.qt import QApplication
        cb = QApplication.clipboard()
        if cb:
            cb.setText(self._text_edit.toPlainText())

    def to_plain_text(self) -> str:
        return self._text_edit.toPlainText()
