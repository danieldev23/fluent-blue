"""Specialized input components: OtpInput and TagInput."""
from __future__ import annotations

from ...compatibility.qt import (
    QHBoxLayout,
    QKeyEvent,
    QLineEdit,
    Qt,
    QToolButton,
    QWidget,
    Signal,
)
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ..base import ThemedMixin, apply_common, check_choice, set_style_prop
from .input import SIZES, VALIDATION_STATES, Input


class _SingleOtpDigit(Input):
    """An individual single-character digit slot for OtpInput."""

    backspace_pressed = Signal()
    paste_event = Signal(str)

    def __init__(self, parent=None, *, size: str = "medium") -> None:
        super().__init__("", parent, size=size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaxLength(1)
        # Use styling to make it square-like
        dim = {"small": 32, "medium": 42, "large": 52}.get(size, 42)
        self.setFixedSize(dim, dim)
        font = ThemeManager.font("heading-2" if size == "large" else "heading-3")
        font.setBold(True)
        self.setFont(font)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802 - Qt override
        if event.key() == Qt.Key.Key_Backspace and not self.text():
            self.backspace_pressed.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class OtpInput(ThemedMixin, QWidget):
    """A multi-slot numeric OTP / 2FA code entry widget with auto-focus and paste support.

    Args:
        length: Number of digit slots (default 6).
        size: ``small``, ``medium``, or ``large``.
        mask: If True, masks characters for PIN codes.
        validation: ``none``, ``error``, ``warning``, or ``success``.
        disabled: Start disabled.
        tooltip: Tooltip text.

    Signals:
        code_changed(str): Emitted whenever digits change.
        completed(str): Emitted when all digits are filled.
    """

    code_changed = Signal(str)
    completed = Signal(str)

    def __init__(
        self,
        parent=None,
        *,
        length: int = 6,
        size: str = "medium",
        mask: bool = False,
        validation: str = "none",
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(parent)
        check_choice("size", size, SIZES)
        self.bind_theme()
        self._length = max(3, min(length, 10))
        self._slots: list[_SingleOtpDigit] = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for i in range(self._length):
            slot = _SingleOtpDigit(self, size=size)
            if mask:
                slot.setEchoMode(QLineEdit.EchoMode.Password)
            slot.textChanged.connect(lambda t, idx=i: self._on_digit_typed(t, idx))
            slot.backspace_pressed.connect(lambda idx=i: self._on_backspace(idx))
            self._slots.append(slot)
            layout.addWidget(slot)

        self.set_validation(validation)
        apply_common(self, disabled=disabled, tooltip=tooltip)

    def _on_digit_typed(self, text: str, idx: int) -> None:
        # Handle multi-character paste into one slot
        if len(text) > 1:
            clean = "".join(filter(str.isalnum, text))
            self.set_code(clean)
            return

        if text and idx < self._length - 1:
            self._slots[idx + 1].setFocus()
            self._slots[idx + 1].selectAll()

        code = self.code()
        self.code_changed.emit(code)
        if len(code) == self._length:
            self.completed.emit(code)

    def _on_backspace(self, idx: int) -> None:
        if idx > 0:
            self._slots[idx - 1].setFocus()
            self._slots[idx - 1].setText("")

    def code(self) -> str:
        """Get the current aggregated code."""
        return "".join(slot.text() for slot in self._slots)

    def set_code(self, code: str) -> None:
        """Fill slots with the provided string."""
        digits = "".join(filter(str.isalnum, str(code)))
        for i, slot in enumerate(self._slots):
            slot.blockSignals(True)
            slot.setText(digits[i] if i < len(digits) else "")
            slot.blockSignals(False)

        current = self.code()
        self.code_changed.emit(current)
        if len(current) == self._length:
            self.completed.emit(current)

    def clear(self) -> None:
        """Clear all digit slots."""
        for slot in self._slots:
            slot.blockSignals(True)
            slot.clear()
            slot.blockSignals(False)
        if self._slots:
            self._slots[0].setFocus()
        self.code_changed.emit("")

    def set_validation(self, state: str) -> None:
        check_choice("validation", state, VALIDATION_STATES)
        for slot in self._slots:
            slot.set_validation(state)

    def setFocus(self) -> None:  # noqa: N802 - Qt override
        if self._slots:
            self._slots[0].setFocus()


class _TagBadge(QWidget):
    """An inline tag pill inside TagInput with a close button."""

    deleted = Signal(str)

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        self._text = text
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 4, 2)
        layout.setSpacing(4)

        from ..display.text import Text
        self._label = Text(text, style="body-small", color="text-primary")
        layout.addWidget(self._label)

        btn = QToolButton(self)
        btn.setIcon(make_icon("close", 10, "text-tertiary"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.deleted.emit(self._text))
        layout.addWidget(btn)

        set_style_prop(self, "fbComponent", "tagBadge")


class TagInput(ThemedMixin, QWidget):
    """An input field that converts typed text into removable tags on Enter or comma.

    Args:
        tags: Initial list of string tags.
        placeholder: Placeholder text when empty.
        max_tags: Maximum allowable tags.
        disabled: Start disabled.
        tooltip: Tooltip text.

    Signals:
        tags_changed(list): List of all tags after add/remove.
        tag_added(str): The added tag.
        tag_removed(str): The removed tag.
    """

    tags_changed = Signal(list)
    tag_added = Signal(str)
    tag_removed = Signal(str)

    def __init__(
        self,
        parent=None,
        *,
        tags: list[str] | None = None,
        placeholder: str = "Type and press Enter...",
        max_tags: int | None = None,
        disabled: bool = False,
        tooltip: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.bind_theme()
        self._tags: list[str] = []
        self._max_tags = max_tags

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 2, 4, 2)
        self._layout.setSpacing(4)

        self._entry = QLineEdit(self)
        self._entry.setPlaceholderText(placeholder)
        self._entry.returnPressed.connect(self._commit_entry)
        self._entry.textEdited.connect(self._on_text_edited)
        self._layout.addWidget(self._entry)

        set_style_prop(self, "fbComponent", "tagInput")
        apply_common(self, disabled=disabled, tooltip=tooltip)

        if tags:
            for t in tags:
                self.add_tag(t)

    def _on_text_edited(self, text: str) -> None:
        if text.endswith(",") or text.endswith(";"):
            clean = text[:-1].strip()
            self._entry.clear()
            if clean:
                self.add_tag(clean)

    def _commit_entry(self) -> None:
        text = self._entry.text().strip()
        if text:
            self._entry.clear()
            self.add_tag(text)

    def add_tag(self, tag: str) -> bool:
        """Add a new tag if not already present."""
        clean = tag.strip()
        if not clean or clean in self._tags:
            return False
        if self._max_tags is not None and len(self._tags) >= self._max_tags:
            return False

        self._tags.append(clean)
        badge = _TagBadge(clean, self)
        badge.deleted.connect(self.remove_tag)

        # Insert before the text entry widget
        idx = self._layout.count() - 1
        self._layout.insertWidget(idx, badge)

        self.tag_added.emit(clean)
        self.tags_changed.emit(list(self._tags))
        return True

    def remove_tag(self, tag: str) -> bool:
        """Remove an existing tag."""
        if tag not in self._tags:
            return False
        idx = self._tags.index(tag)
        self._tags.remove(tag)

        # Find widget at index
        item = self._layout.itemAt(idx)
        if item and item.widget():
            item.widget().deleteLater()

        self.tag_removed.emit(tag)
        self.tags_changed.emit(list(self._tags))
        return True

    def tags(self) -> list[str]:
        return list(self._tags)

    def clear(self) -> None:
        for t in list(self._tags):
            self.remove_tag(t)

