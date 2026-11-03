"""FormField and InputGroup: compose inputs with labels, messages and addons."""
from __future__ import annotations

from ...compatibility.qt import QEvent, QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget, Signal
from ..base import set_style_prop


class FieldLabel(QLabel):
    """The label of a :class:`FormField`."""


class FieldMessage(QLabel):
    """Helper or validation text under a field."""


class FormField(QWidget):
    """Label, control, helper text and error message as one unit.

    Args:
        label: Field label, linked to the control as its buddy for keyboard access.
        control: The input widget.
        helper: Helper text shown when there is no error.
        required: Append a required marker to the label.
        validator: Optional ``callable(value) -> str | None`` returning an error message.
            It runs on ``validate()`` and when an input finishes editing.

    Signals:
        validated(bool): Emitted after validation with the outcome.
    """

    validated = Signal(bool)

    def __init__(self, label: str = "", control=None, parent=None, *, helper: str = "", required: bool = False,
                 validator=None) -> None:
        super().__init__(parent)
        self._helper = helper
        self._validator = validator
        self._error = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.label = FieldLabel(f"{label} *" if required else label)
        self.label.setVisible(bool(label))
        self.message = FieldMessage(helper)
        self.message.setWordWrap(True)
        self.message.setVisible(bool(helper))
        layout.addWidget(self.label)
        self.control = control
        if control is not None:
            layout.addWidget(control)
            self.label.setBuddy(control)
            if label and not control.accessibleName():
                control.setAccessibleName(label)
            if hasattr(control, "editingFinished") and validator:
                control.editingFinished.connect(self.validate)
        layout.addWidget(self.message)
        layout.addStretch(1)

    def error(self) -> str:
        return self._error

    def set_error(self, message: str = "") -> None:
        """Show an error, or clear it with an empty message."""
        self._error = message
        if self.control is not None and hasattr(self.control, "set_validation"):
            self.control.set_validation("error" if message else "none")
        set_style_prop(self.message, "state", "error" if message else "none")
        self.message.setText(message or self._helper)
        self.message.setVisible(bool(message or self._helper))
        self.setAccessibleDescription(message)

    def set_helper(self, helper: str) -> None:
        self._helper = helper
        if not self._error:
            self.message.setText(helper)
            self.message.setVisible(bool(helper))

    def validate(self) -> bool:
        """Run the validator and show its result. Returns ``True`` when the value is valid."""
        if self._validator is None or self.control is None:
            return True
        control = self.control
        value = control.text() if hasattr(control, "text") else control.value()
        message = self._validator(value) or ""
        self.set_error(message)
        self.validated.emit(not message)
        return not message


class InputGroup(QFrame):
    """Joins an input with text or widget addons inside a single border.

    Args:
        control: The central input.
        prefix: Leading text or widget.
        suffix: Trailing text or widget.
    """

    def __init__(self, control=None, parent=None, *, prefix=None, suffix=None) -> None:
        super().__init__(parent)
        self.control = control
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(0)
        if prefix is not None:
            layout.addWidget(self._addon(prefix, "start"))
        if control is not None:
            layout.addWidget(control, 1)
            control.installEventFilter(self)
        if suffix is not None:
            layout.addWidget(self._addon(suffix, "end"))

    def _addon(self, addon, side: str):
        if isinstance(addon, str):
            label = QLabel(addon)
            label.setProperty("addon", True)
            label.setProperty("side", side)
            return label
        return addon

    def eventFilter(self, watched, event) -> bool:  # noqa: N802 - Qt override
        if event.type() in (QEvent.Type.FocusIn, QEvent.Type.FocusOut):
            set_style_prop(self, "focused", "true" if event.type() == QEvent.Type.FocusIn else "false")
        return super().eventFilter(watched, event)
