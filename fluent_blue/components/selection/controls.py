"""Checkbox, RadioButton, RadioGroup, Switch, SegmentedControl, Slider and SpinBox."""
from __future__ import annotations

from ...compatibility.qt import (
    Property, QAbstractButton, QButtonGroup, QCheckBox, QColor, QHBoxLayout, QPainter, QPen, QPropertyAnimation, QPushButton,
    QRadioButton, QRectF, QSize, QSizePolicy, QSlider, QSpinBox, Qt, QVBoxLayout, QWidget, Signal,
)
from ...core.theme_manager import ThemeManager
from ..base import ThemedMixin, apply_common, check_choice, normalize_options


class Checkbox(QCheckBox):
    """A checkbox, with optional indeterminate state.

    Args:
        text: Label.
        checked: Initial state.
        indeterminate: Start in the mixed state; also enables tristate cycling.
        disabled: Start disabled.

    Signals:
        Inherits ``toggled(bool)`` and ``stateChanged(int)`` from ``QCheckBox``.
    """

    def __init__(self, text: str = "", parent=None, *, checked: bool = False, indeterminate: bool = False,
                 disabled: bool = False, tooltip: str | None = None) -> None:
        super().__init__(text, parent)
        ThemeManager.ensure_applied()
        self.setChecked(checked)
        if indeterminate:
            self.setTristate(True)
            self.setCheckState(Qt.CheckState.PartiallyChecked)
        apply_common(self, disabled=disabled, tooltip=tooltip)


class RadioButton(QRadioButton):
    """A radio button. Use :class:`RadioGroup` for the common case.

    Args:
        text: Label.
        checked: Initial state.
        disabled: Start disabled.
    """

    def __init__(self, text: str = "", parent=None, *, checked: bool = False, disabled: bool = False,
                 tooltip: str | None = None) -> None:
        super().__init__(text, parent)
        ThemeManager.ensure_applied()
        self.setChecked(checked)
        apply_common(self, disabled=disabled, tooltip=tooltip)


class RadioGroup(QWidget):
    """A set of mutually exclusive radio buttons.

    Args:
        options: Entries, in the same forms as ``Select``.
        value: Initial value.
        orientation: ``vertical`` or ``horizontal``.
        disabled: Start disabled.

    Signals:
        value_changed(object): The newly selected value.
    """

    value_changed = Signal(object)

    def __init__(self, options=None, parent=None, *, value=None, orientation: str = "vertical", disabled: bool = False) -> None:
        super().__init__(parent)
        check_choice("orientation", orientation, ("vertical", "horizontal"))
        layout = QVBoxLayout(self) if orientation == "vertical" else QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8 if orientation == "vertical" else 16)
        self._group = QButtonGroup(self)
        self._values: dict = {}
        for label, option in normalize_options(options):
            button = RadioButton(label)
            self._values[button] = option
            self._group.addButton(button)
            layout.addWidget(button)
            button.setChecked(option == value)
            button.toggled.connect(lambda on, b=button: on and self.value_changed.emit(self._values[b]))
        self.setDisabled(disabled)

    def value(self):
        button = self._group.checkedButton()
        return self._values[button] if button else None

    def set_value(self, value) -> None:
        """Select by value. Raises ``ValueError`` for an unknown value."""
        for button, option in self._values.items():
            if option == value:
                button.setChecked(True)
                return
        raise ValueError(f"{value!r} is not an option of this RadioGroup.")


class Switch(ThemedMixin, QAbstractButton):
    """An animated on/off toggle.

    Args:
        text: Optional label to the right of the track.
        checked: Initial state.
        disabled: Start disabled.

    Signals:
        Inherits ``toggled(bool)`` from ``QAbstractButton``.
    """

    TRACK_W, TRACK_H = 34, 20

    def __init__(self, text: str = "", parent=None, *, checked: bool = False, disabled: bool = False,
                 tooltip: str | None = None) -> None:
        super().__init__(parent)
        self._position = 1.0 if checked else 0.0
        self.setText(text)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.bind_theme()
        self._anim = QPropertyAnimation(self, b"position", self)
        self.toggled.connect(self._animate)
        apply_common(self, disabled=disabled, tooltip=tooltip, accessible_name=text or None)

    def _get_position(self) -> float:
        return self._position

    def _set_position(self, value: float) -> None:
        self._position = value
        self.update()

    position = Property(float, _get_position, _set_position)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        width = self.TRACK_W + 4
        if self.text():
            self.ensurePolished()
            width += 8 + self.fontMetrics().horizontalAdvance(self.text())
        return QSize(width, max(24, self.fontMetrics().height()))

    def hitButton(self, pos) -> bool:  # noqa: N802 - Qt override
        return self.rect().contains(pos)

    def _animate(self, checked: bool) -> None:
        end = 1.0 if checked else 0.0
        duration = ThemeManager.duration("normal")
        if duration <= 0 or not self.isVisible():
            self._anim.stop()
            self._set_position(end)
            return
        self._anim.stop()
        self._anim.setDuration(duration)
        self._anim.setEasingCurve(ThemeManager.easing())
        self._anim.setStartValue(self._position)
        self._anim.setEndValue(end)
        self._anim.start()

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        enabled, hovered = self.isEnabled(), self.underMouse()
        top = (self.height() - self.TRACK_H) / 2
        track = QRectF(2, top, self.TRACK_W, self.TRACK_H)
        on = ThemeManager.qcolor("primary-hover" if hovered else "primary")
        off = ThemeManager.qcolor("border-strong")
        if not enabled:
            on, off = ThemeManager.qcolor("border"), ThemeManager.qcolor("border-subtle")
        t = self._position
        color = QColor(
            round(off.red() + (on.red() - off.red()) * t),
            round(off.green() + (on.green() - off.green()) * t),
            round(off.blue() + (on.blue() - off.blue()) * t),
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawRoundedRect(track, self.TRACK_H / 2, self.TRACK_H / 2)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(ThemeManager.qcolor("border-focus"), 2))
            painter.drawRoundedRect(track.adjusted(-1, -1, 1, 1), self.TRACK_H / 2 + 1, self.TRACK_H / 2 + 1)
            painter.setPen(Qt.PenStyle.NoPen)
        knob = self.TRACK_H - 6
        x = track.left() + 3 + (self.TRACK_W - 6 - knob) * t
        painter.setBrush(ThemeManager.qcolor("gray-0" if enabled else "surface-tertiary"))
        painter.drawEllipse(QRectF(x, top + 3, knob, knob))
        if self.text():
            painter.setPen(ThemeManager.qcolor("text-primary" if enabled else "text-disabled"))
            text_rect = self.rect().adjusted(self.TRACK_W + 12, 0, 0, 0)
            painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft), self.text())
        painter.end()


class SegmentedControl(QWidget):
    """A compact, mutually exclusive option strip.

    Args:
        options: Entries, in the same forms as ``Select``.
        value: Initial value; defaults to the first option.
        disabled: Start disabled.

    Signals:
        value_changed(object): The newly selected value.
    """

    value_changed = Signal(object)

    def __init__(self, options=None, parent=None, *, value=None, disabled: bool = False) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        ThemeManager.ensure_applied()
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        self._group = QButtonGroup(self)
        self._values: dict = {}
        entries = normalize_options(options)
        if value is None and entries:
            value = entries[0][1]
        for label, option in entries:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setChecked(option == value)
            self._group.addButton(button)
            self._values[button] = option
            layout.addWidget(button)
            button.toggled.connect(lambda on, b=button: on and self.value_changed.emit(self._values[b]))
        self.setDisabled(disabled)

    def value(self):
        button = self._group.checkedButton()
        return self._values[button] if button else None

    def set_value(self, value) -> None:
        """Select by value. Raises ``ValueError`` for an unknown value."""
        for button, option in self._values.items():
            if option == value:
                button.setChecked(True)
                return
        raise ValueError(f"{value!r} is not an option of this SegmentedControl.")


class Slider(QSlider):
    """A value slider.

    Args:
        value: Initial value.
        minimum: Lower bound.
        maximum: Upper bound.
        step: Single-step amount for arrow keys.
        orientation: ``horizontal`` or ``vertical``.
        disabled: Start disabled.

    Signals:
        Inherits ``valueChanged(int)`` and ``sliderReleased`` from ``QSlider``.
    """

    def __init__(self, value: int = 0, parent=None, *, minimum: int = 0, maximum: int = 100, step: int = 1,
                 orientation: str = "horizontal", disabled: bool = False, tooltip: str | None = None) -> None:
        check_choice("orientation", orientation, ("horizontal", "vertical"))
        super().__init__(Qt.Orientation.Horizontal if orientation == "horizontal" else Qt.Orientation.Vertical, parent)
        ThemeManager.ensure_applied()
        self.setRange(minimum, maximum)
        self.setSingleStep(step)
        self.setValue(value)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_common(self, disabled=disabled, tooltip=tooltip)


class SpinBox(QSpinBox):
    """An integer input with stepper buttons.

    Args:
        value: Initial value.
        minimum: Lower bound.
        maximum: Upper bound.
        step: Step amount.
        suffix: Text after the value, such as ``" px"``.
        disabled: Start disabled.

    Signals:
        Inherits ``valueChanged(int)`` from ``QSpinBox``.
    """

    def __init__(self, value: int = 0, parent=None, *, minimum: int = 0, maximum: int = 100, step: int = 1,
                 suffix: str = "", disabled: bool = False, tooltip: str | None = None) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        self.setRange(minimum, maximum)
        self.setSingleStep(step)
        self.setValue(value)
        self.setSuffix(suffix)
        apply_common(self, disabled=disabled, tooltip=tooltip)
