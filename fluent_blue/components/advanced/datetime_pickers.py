"""Calendar, DatePicker and TimePicker. The public API uses ``datetime.date`` and ``datetime.time``."""
from __future__ import annotations

import calendar as _calendar
import datetime as dt

from ...compatibility.qt import (
    QHBoxLayout, QListWidget, QPainter, QRectF, QSize, Qt, QVBoxLayout, QWidget, Signal,
)
from ...core.theme_manager import ThemeManager
from ..base import ThemedMixin
from ..buttons.button import IconButton
from ..display.text import Text
from ..inputs.input import Input
from ..popup import PopupShell

_WEEKDAYS = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
_CELL = 34
_HEAD = 26


class _DayGrid(QWidget):
    """Paints one month. Hover, selection and today are read at paint time."""

    def __init__(self, owner) -> None:
        super().__init__()
        self.owner = owner
        self._hover: dt.date | None = None
        self.setMouseTracking(True)
        self.setFixedSize(_CELL * 7, _HEAD + _CELL * 6)

    def date_at(self, pos) -> dt.date | None:
        if pos.y() < _HEAD:
            return None
        column, row = pos.x() // _CELL, (pos.y() - _HEAD) // _CELL
        if not (0 <= column < 7 and 0 <= row < 6):
            return None
        return self.owner.first_visible_day() + dt.timedelta(days=row * 7 + column)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        self._hover = self.date_at(event.position().toPoint())
        self.update()

    def leaveEvent(self, _event) -> None:  # noqa: N802 - Qt override
        self._hover = None
        self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        day = self.date_at(event.position().toPoint())
        if day:
            self.owner.select(day)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        owner = self.owner
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(ThemeManager.font("caption"))
        painter.setPen(ThemeManager.qcolor("text-tertiary"))
        for index, name in enumerate(_WEEKDAYS):
            painter.drawText(QRectF(index * _CELL, 0, _CELL, _HEAD), Qt.AlignmentFlag.AlignCenter, name)
        body, strong = ThemeManager.font("body-medium"), ThemeManager.font("heading-6")
        start, today = owner.first_visible_day(), dt.date.today()
        for offset in range(42):
            day = start + dt.timedelta(days=offset)
            cell = QRectF((offset % 7) * _CELL + 2, _HEAD + (offset // 7) * _CELL + 2, _CELL - 4, _CELL - 4)
            selected = day == owner.selected_date()
            enabled = owner.is_enabled_date(day)
            painter.setPen(Qt.PenStyle.NoPen)
            if selected:
                painter.setBrush(ThemeManager.qcolor("primary"))
                painter.drawRoundedRect(cell, 6, 6)
            elif day == self._hover and enabled:
                painter.setBrush(ThemeManager.qcolor("ghost-hover"))
                painter.drawRoundedRect(cell, 6, 6)
            if day == owner.cursor_date() and owner.hasFocus():
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(ThemeManager.qcolor("border-focus"))
                painter.drawRoundedRect(cell, 6, 6)
            if selected:
                color = "on-primary"
            elif not enabled:
                color = "text-disabled"
            elif day == today:
                color = "primary-text"
            elif day.month != owner.visible_month()[1]:
                color = "text-tertiary"
            else:
                color = "text-primary"
            painter.setFont(strong if day == today or selected else body)
            painter.setPen(ThemeManager.qcolor(color))
            painter.drawText(cell, Qt.AlignmentFlag.AlignCenter, str(day.day))
        painter.end()


class Calendar(ThemedMixin, QWidget):
    """A month view. Arrow keys move, Enter selects and Page Up/Down change the month.

    Args:
        selected: Initially selected date.
        minimum: Earliest selectable date.
        maximum: Latest selectable date.

    Signals:
        date_selected(object): The chosen ``datetime.date``.
        month_changed(int, int): The visible year and month.
    """

    date_selected = Signal(object)
    month_changed = Signal(int, int)

    def __init__(self, parent=None, *, selected: dt.date | None = None, minimum: dt.date | None = None,
                 maximum: dt.date | None = None) -> None:
        super().__init__(parent)
        self._selected, self._minimum, self._maximum = selected, minimum, maximum
        self._cursor = selected or dt.date.today()
        self._year, self._month = self._cursor.year, self._cursor.month
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Calendar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        header = QHBoxLayout()
        self._prev = IconButton("chevron-left", size="small", tooltip="Previous month")
        self._next = IconButton("chevron-right", size="small", tooltip="Next month")
        self._title = Text("", style="heading-6")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._prev.clicked.connect(lambda: self.shift_month(-1))
        self._next.clicked.connect(lambda: self.shift_month(1))
        header.addWidget(self._prev)
        header.addWidget(self._title, 1)
        header.addWidget(self._next)
        layout.addLayout(header)
        self.grid = _DayGrid(self)
        layout.addWidget(self.grid)
        self.setSizePolicy(self.sizePolicy().Policy.Fixed, self.sizePolicy().Policy.Fixed)
        self.bind_theme()
        self._sync_title()

    def selected_date(self) -> dt.date | None:
        return self._selected

    def cursor_date(self) -> dt.date:
        return self._cursor

    def visible_month(self) -> tuple[int, int]:
        return self._year, self._month

    def first_visible_day(self) -> dt.date:
        """The Monday on or before the first of the visible month."""
        first = dt.date(self._year, self._month, 1)
        return first - dt.timedelta(days=first.weekday())

    def is_enabled_date(self, day: dt.date) -> bool:
        return (self._minimum is None or day >= self._minimum) and (self._maximum is None or day <= self._maximum)

    def set_selected_date(self, day: dt.date | None) -> None:
        """Select a date programmatically, without emitting ``date_selected``."""
        self._selected = day
        if day:
            self._cursor = day
            self._show_month(day.year, day.month)
        self.grid.update()

    def select(self, day: dt.date) -> None:
        """Select a date as if chosen by the user. Dates out of range are ignored."""
        if not self.is_enabled_date(day):
            return
        self._selected = self._cursor = day
        self._show_month(day.year, day.month)
        self.grid.update()
        self.date_selected.emit(day)

    def shift_month(self, delta: int) -> None:
        """Move the visible month."""
        total = self._year * 12 + self._month - 1 + delta
        self._show_month(total // 12, total % 12 + 1)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        key = event.key()
        moves = {Qt.Key.Key_Left: -1, Qt.Key.Key_Right: 1, Qt.Key.Key_Up: -7, Qt.Key.Key_Down: 7}
        if key in moves:
            self._move_cursor(self._cursor + dt.timedelta(days=moves[key]))
        elif key in (Qt.Key.Key_PageUp, Qt.Key.Key_PageDown):
            total = self._cursor.year * 12 + self._cursor.month - 1 + (-1 if key == Qt.Key.Key_PageUp else 1)
            year, month = total // 12, total % 12 + 1
            last = _calendar.monthrange(year, month)[1]
            self._move_cursor(dt.date(year, month, min(self._cursor.day, last)))
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.select(self._cursor)
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().focusInEvent(event)
        self.grid.update()

    def focusOutEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().focusOutEvent(event)
        self.grid.update()

    def _move_cursor(self, day: dt.date) -> None:
        self._cursor = day
        self._show_month(day.year, day.month)
        self.grid.update()

    def _show_month(self, year: int, month: int) -> None:
        if (year, month) != (self._year, self._month):
            self._year, self._month = year, month
            self._sync_title()
            self.grid.update()
            self.month_changed.emit(year, month)

    def _sync_title(self) -> None:
        self._title.setText(f"{_calendar.month_name[self._month]} {self._year}")


class _PickerInput(Input):
    """A read-only input that opens a popup by mouse or keyboard."""

    def __init__(self, parent, *, placeholder, icon, **kwargs) -> None:
        kwargs.setdefault("clearable", True)
        super().__init__("", parent, placeholder=placeholder, suffix_icon=icon, **kwargs)
        self.setReadOnly(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.popup = None

    def open_popup(self) -> None:
        raise NotImplementedError

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().mousePressEvent(event)
        if self.isEnabled():
            self.open_popup()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
            self.open_popup()
        elif event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self.clear_text()
        else:
            super().keyPressEvent(event)

    def _sync_clear(self, text: str) -> None:
        self._clear_action.setVisible(bool(text))


class DatePicker(_PickerInput):
    """A date field with a popup calendar.

    Args:
        date: Initial ``datetime.date``.
        display_format: ``strftime`` format for the text.
        minimum: Earliest selectable date.
        maximum: Latest selectable date.
        placeholder: Placeholder text.

    Signals:
        date_changed(object): The new date, or ``None`` when cleared.
    """

    date_changed = Signal(object)

    def __init__(self, parent=None, *, date: dt.date | None = None, display_format: str = "%Y-%m-%d",
                 minimum: dt.date | None = None, maximum: dt.date | None = None, placeholder: str = "Select date",
                 **kwargs) -> None:
        super().__init__(parent, placeholder=placeholder, icon="calendar", **kwargs)
        self._format, self._minimum, self._maximum = display_format, minimum, maximum
        self._date = None
        self.cleared.connect(lambda: self.set_date(None))
        self.set_date(date)

    def date(self) -> dt.date | None:
        return self._date

    def set_date(self, date: dt.date | None) -> None:
        """Set the date and emit ``date_changed`` if it changed."""
        self.setText(date.strftime(self._format) if date else "")
        if date != self._date:
            self._date = date
            self.date_changed.emit(date)

    def open_popup(self) -> None:
        if self.popup is None:
            self.popup = PopupShell(self, padding=10)
            self.calendar = Calendar(minimum=self._minimum, maximum=self._maximum)
            self.calendar.date_selected.connect(self._chosen)
            self.popup.body.addWidget(self.calendar)
        self.calendar.set_selected_date(self._date)
        self.popup.adjustSize()
        self.popup.show_at(self)
        self.calendar.setFocus()

    def _chosen(self, day: dt.date) -> None:
        self.set_date(day)
        self.popup.hide()
        self.setFocus()


class TimePopup(PopupShell):
    """Hour and minute columns used by :class:`TimePicker`."""

    def __init__(self, parent, minute_step: int) -> None:
        super().__init__(parent, padding=6)
        row = QHBoxLayout()
        row.setSpacing(4)
        self.hours = QListWidget()
        self.minutes = QListWidget()
        self.hours.addItems([f"{h:02d}" for h in range(24)])
        self.minutes.addItems([f"{m:02d}" for m in range(0, 60, minute_step)])
        for column, name in ((self.hours, "Hour"), (self.minutes, "Minute")):
            column.setFixedSize(QSize(60, 200))
            column.setAccessibleName(name)
            row.addWidget(column)
        self.body.addLayout(row)


class TimePicker(_PickerInput):
    """A time field with hour and minute columns.

    Args:
        time: Initial ``datetime.time``.
        minute_step: Minute granularity.
        display_format: ``strftime`` format for the text.
        placeholder: Placeholder text.

    Signals:
        time_changed(object): The new time, or ``None`` when cleared.
    """

    time_changed = Signal(object)

    def __init__(self, parent=None, *, time: dt.time | None = None, minute_step: int = 5, display_format: str = "%H:%M",
                 placeholder: str = "Select time", **kwargs) -> None:
        super().__init__(parent, placeholder=placeholder, icon="clock", **kwargs)
        self._format, self._step = display_format, max(1, minute_step)
        self._time = None
        self.cleared.connect(lambda: self.set_time(None))
        self.set_time(time)

    def time(self) -> dt.time | None:
        return self._time

    def set_time(self, time: dt.time | None) -> None:
        """Set the time and emit ``time_changed`` if it changed."""
        self.setText(time.strftime(self._format) if time else "")
        if time != self._time:
            self._time = time
            self.time_changed.emit(time)

    def open_popup(self) -> None:
        if self.popup is None:
            self.popup = TimePopup(self, self._step)
            self.popup.hours.itemClicked.connect(lambda _item: self._apply())
            self.popup.minutes.itemClicked.connect(lambda _item: self._apply())
            self.popup.hours.itemActivated.connect(lambda _item: self._apply())
            self.popup.minutes.itemActivated.connect(lambda _item: self._apply(close=True))
        current = self._time or dt.time(9, 0)
        self.popup.hours.setCurrentRow(current.hour)
        self.popup.minutes.setCurrentRow(current.minute // self._step)
        self.popup.hours.scrollToItem(self.popup.hours.currentItem())
        self.popup.minutes.scrollToItem(self.popup.minutes.currentItem())
        self.popup.adjustSize()
        self.popup.show_at(self)
        self.popup.hours.setFocus()

    def _apply(self, close: bool = False) -> None:
        hour = max(0, self.popup.hours.currentRow())
        minute = max(0, self.popup.minutes.currentRow()) * self._step
        self.set_time(dt.time(hour, minute))
        if close:
            self.popup.hide()
            self.setFocus()
