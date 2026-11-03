"""Single-line inputs. ``Input`` extends ``QLineEdit``, so the whole Qt API stays available."""
from __future__ import annotations

from ...compatibility.qt import QAction, QDoubleValidator, QLineEdit, QPlainTextEdit, Qt, QTimer, Signal
from ...icons import icon as make_icon
from ..base import ThemedMixin, apply_common, check_choice, set_style_prop

VALIDATION_STATES = ("none", "error", "warning", "success")
SIZES = ("small", "medium", "large")


class Input(ThemedMixin, QLineEdit):
    """A text input with icons, a clear button and validation state.

    Args:
        text: Initial text.
        placeholder: Placeholder text.
        size: ``small``, ``medium`` or ``large``.
        prefix_icon: Icon name at the start.
        suffix_icon: Icon name at the end.
        clearable: Show a clear button while the field has text.
        validation: ``none``, ``error``, ``warning`` or ``success``.
        read_only: Selectable but not editable.
        disabled: Start disabled.
        tooltip: Tooltip text.
        accessible_name: Name for assistive technology; defaults to the placeholder.

    Signals:
        cleared: The clear button was used.
        Inherits ``textChanged``, ``editingFinished`` and ``returnPressed`` from ``QLineEdit``.
    """

    cleared = Signal()

    def __init__(self, text: str = "", parent=None, *, placeholder: str = "", size: str = "medium",
                 prefix_icon: str | None = None, suffix_icon: str | None = None, clearable: bool = False,
                 validation: str = "none", read_only: bool = False, disabled: bool = False,
                 tooltip: str | None = None, accessible_name: str | None = None) -> None:
        super().__init__(text, parent)
        self._prefix_name = prefix_icon
        self._suffix_name = suffix_icon
        self._prefix_action = self._suffix_action = self._clear_action = None
        self._clearable = clearable
        self.bind_theme()
        self.setPlaceholderText(placeholder)
        check_choice("size", size, SIZES)
        self.setProperty("fbSize", size)
        self.set_validation(validation)
        self.setReadOnly(read_only)
        apply_common(self, disabled=disabled, tooltip=tooltip, accessible_name=accessible_name or placeholder or None)
        if prefix_icon:
            self._prefix_action = self.addAction(make_icon(prefix_icon, 16, "text-tertiary"), QLineEdit.ActionPosition.LeadingPosition)
        if suffix_icon:
            self._suffix_action = self.addAction(make_icon(suffix_icon, 16, "text-tertiary"), QLineEdit.ActionPosition.TrailingPosition)
        if clearable:
            self._clear_action = QAction(make_icon("close", 14, "text-tertiary"), "Clear", self)
            self._clear_action.triggered.connect(self.clear_text)
            self.addAction(self._clear_action, QLineEdit.ActionPosition.TrailingPosition)
            self.textChanged.connect(self._sync_clear)
            self._sync_clear(text)

    def validation(self) -> str:
        return self.property("validation")

    def set_validation(self, state: str) -> None:
        """Set the validation state, which changes the border color."""
        check_choice("validation", state, VALIDATION_STATES)
        set_style_prop(self, "validation", state)

    def clear_text(self) -> None:
        """Clear the field, emit ``cleared`` and keep focus."""
        self.clear()
        self.setFocus()
        self.cleared.emit()

    def refresh_theme(self) -> None:
        if self._prefix_action:
            self._prefix_action.setIcon(make_icon(self._prefix_name, 16, "text-tertiary"))
        if self._suffix_action:
            self._suffix_action.setIcon(make_icon(self._suffix_name, 16, "text-tertiary"))
        if self._clear_action:
            self._clear_action.setIcon(make_icon("close", 14, "text-tertiary"))

    def _sync_clear(self, text: str) -> None:
        self._clear_action.setVisible(bool(text) and not self.isReadOnly())


class ClearableInput(Input):
    """An ``Input`` with the clear button on by default."""

    def __init__(self, text: str = "", parent=None, **kwargs) -> None:
        kwargs.setdefault("clearable", True)
        super().__init__(text, parent, **kwargs)


class PasswordInput(Input):
    """A masked input with a visibility toggle.

    Signals:
        visibility_changed(bool): ``True`` when the password is shown.
    """

    visibility_changed = Signal(bool)

    def __init__(self, text: str = "", parent=None, *, placeholder: str = "Password", **kwargs) -> None:
        kwargs.setdefault("prefix_icon", "lock")
        super().__init__(text, parent, placeholder=placeholder, **kwargs)
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self._toggle = QAction(make_icon("eye", 16, "text-tertiary"), "Show password", self)
        self._toggle.triggered.connect(self.toggle_visibility)
        self.addAction(self._toggle, QLineEdit.ActionPosition.TrailingPosition)

    def is_revealed(self) -> bool:
        return self.echoMode() == QLineEdit.EchoMode.Normal

    def toggle_visibility(self) -> None:
        """Toggle between masked and plain text."""
        reveal = not self.is_revealed()
        self.setEchoMode(QLineEdit.EchoMode.Normal if reveal else QLineEdit.EchoMode.Password)
        self._toggle.setText("Hide password" if reveal else "Show password")
        self.refresh_theme()
        self.visibility_changed.emit(reveal)

    def refresh_theme(self) -> None:
        super().refresh_theme()
        if hasattr(self, "_toggle"):
            self._toggle.setIcon(make_icon("eye-off" if self.is_revealed() else "eye", 16, "text-tertiary"))


class SearchInput(Input):
    """A clearable search field that debounces typing.

    Args:
        debounce_ms: Quiet time before ``search_changed`` fires; 0 fires on every keystroke.

    Signals:
        search_changed(str): The settled query.
    """

    search_changed = Signal(str)

    def __init__(self, text: str = "", parent=None, *, placeholder: str = "Search…", debounce_ms: int = 200, **kwargs) -> None:
        kwargs.setdefault("prefix_icon", "search")
        kwargs.setdefault("clearable", True)
        super().__init__(text, parent, placeholder=placeholder, **kwargs)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(max(0, debounce_ms))
        self._timer.timeout.connect(lambda: self.search_changed.emit(self.text()))
        self.textChanged.connect(lambda _text: self._timer.start())
        self.cleared.connect(self._flush)
        self.returnPressed.connect(self._flush)

    def _flush(self) -> None:
        self._timer.stop()
        self.search_changed.emit(self.text())


class NumberInput(Input):
    """A numeric input with bounds, steppers and arrow key support.

    Args:
        value: Initial value.
        minimum: Lower bound.
        maximum: Upper bound.
        step: Amount added by the steppers and arrow keys.
        decimals: Digits after the decimal point.

    Signals:
        value_changed(float): The committed numeric value changed.
    """

    value_changed = Signal(float)

    def __init__(self, value: float = 0, parent=None, *, minimum: float = -1e12, maximum: float = 1e12, step: float = 1,
                 decimals: int = 0, **kwargs) -> None:
        super().__init__("", parent, **kwargs)
        self._minimum, self._maximum, self._step, self._decimals = minimum, maximum, step, decimals
        self._value = None
        validator = QDoubleValidator(minimum, maximum, decimals, self)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.setValidator(validator)
        self._plus = QAction(make_icon("plus", 14, "text-secondary"), "Increase", self)
        self._minus = QAction(make_icon("minus", 14, "text-secondary"), "Decrease", self)
        self._plus.triggered.connect(lambda: self.step_by(1))
        self._minus.triggered.connect(lambda: self.step_by(-1))
        self.addAction(self._minus, QLineEdit.ActionPosition.TrailingPosition)
        self.addAction(self._plus, QLineEdit.ActionPosition.TrailingPosition)
        self.editingFinished.connect(self._commit)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.set_value(value)

    def value(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        """Set the value, clamped to the bounds. Emits ``value_changed`` if it changed."""
        value = round(min(max(float(value), self._minimum), self._maximum), self._decimals)
        self.setText(f"{value:.{self._decimals}f}")
        if value != self._value:
            self._value = value
            self.value_changed.emit(value)

    def step_by(self, steps: int) -> None:
        """Move the value by a number of steps."""
        self._commit()
        self.set_value(self._value + steps * self._step)

    def refresh_theme(self) -> None:
        super().refresh_theme()
        if hasattr(self, "_plus"):
            self._plus.setIcon(make_icon("plus", 14, "text-secondary"))
            self._minus.setIcon(make_icon("minus", 14, "text-secondary"))

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() == Qt.Key.Key_Up:
            self.step_by(1)
        elif event.key() == Qt.Key.Key_Down:
            self.step_by(-1)
        else:
            super().keyPressEvent(event)

    def _commit(self) -> None:
        try:
            self.set_value(float(self.text()))
        except ValueError:
            self.set_value(self._value if self._value is not None else max(self._minimum, 0))


class TextArea(ThemedMixin, QPlainTextEdit):
    """A multi-line plain text input.

    Args:
        text: Initial text.
        placeholder: Placeholder text.
        max_length: Hard limit on length in characters; ``None`` for no limit.
        rows: Approximate visible rows, used for the minimum height.
        validation: ``none``, ``error``, ``warning`` or ``success``.
        read_only: Selectable but not editable.
        disabled: Start disabled.

    Signals:
        text_changed(str): The new content.
    """

    text_changed = Signal(str)

    def __init__(self, text: str = "", parent=None, *, placeholder: str = "", max_length: int | None = None,
                 rows: int = 4, validation: str = "none", read_only: bool = False, disabled: bool = False,
                 tooltip: str | None = None) -> None:
        super().__init__(text, parent)
        self._max_length = max_length
        self.bind_theme()
        self.setPlaceholderText(placeholder)
        self.setTabChangesFocus(True)
        self.setReadOnly(read_only)
        self.setMinimumHeight(rows * 20 + 16)
        self.set_validation(validation)
        apply_common(self, disabled=disabled, tooltip=tooltip, accessible_name=placeholder or None)
        self.textChanged.connect(self._on_text_changed)

    def text(self) -> str:
        return self.toPlainText()

    def set_text(self, text: str) -> None:
        self.setPlainText(text)

    def validation(self) -> str:
        return self.property("validation")

    def set_validation(self, state: str) -> None:
        check_choice("validation", state, VALIDATION_STATES)
        set_style_prop(self, "validation", state)

    def _on_text_changed(self) -> None:
        text = self.toPlainText()
        if self._max_length is not None and len(text) > self._max_length:
            cursor = self.textCursor()
            position = min(cursor.position(), self._max_length)
            self.blockSignals(True)
            self.setPlainText(text[:self._max_length])
            cursor = self.textCursor()
            cursor.setPosition(position)
            self.setTextCursor(cursor)
            self.blockSignals(False)
            text = text[:self._max_length]
        self.text_changed.emit(text)
