"""Select, ComboBox and MultiSelect."""
from __future__ import annotations

from ...compatibility.qt import (
    QComboBox,
    QCompleter,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPainter,
    QPushButton,
    QSize,
    Qt,
    Signal,
)
from ...icons import icon_pixmap
from ..base import ThemedMixin, apply_common, check_choice, normalize_options, set_style_prop
from ..popup import PopupShell


class Select(ThemedMixin, QComboBox):
    """Choose one value from a list.

    Args:
        options: ``"a"``, ``("Label", value)`` or ``{"label": ..., "value": ...}`` entries.
        value: Initial value.
        placeholder: Text shown while nothing is selected.
        size: ``small``, ``medium`` or ``large``.
        disabled: Start disabled.

    Signals:
        value_changed(object): The newly selected value.
    """

    value_changed = Signal(object)
    _EDITABLE = False

    def __init__(self, options=None, parent=None, *, value=None, placeholder: str = "", size: str = "medium",
                 disabled: bool = False, tooltip: str | None = None) -> None:
        super().__init__(parent)
        self.bind_theme()
        check_choice("size", size, ("small", "medium", "large"))
        self.setProperty("fbSize", size)
        self.setEditable(self._EDITABLE)
        view = QListView()
        self.setView(view)
        # A frameless translucent popup lets the stylesheet's rounded corners show.
        popup = view.window()
        popup.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        popup.setWindowFlag(Qt.WindowType.NoDropShadowWindowHint)
        popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(6)
        self.setPlaceholderText(placeholder)
        self.set_options(options or [])
        if value is not None:
            self.set_value(value)
        elif placeholder and not self._EDITABLE:
            self.setCurrentIndex(-1)
        self.currentIndexChanged.connect(self._emit_value)
        apply_common(self, disabled=disabled, tooltip=tooltip, accessible_name=placeholder or None)

    def set_options(self, options) -> None:
        """Replace the options without emitting ``value_changed``."""
        self.blockSignals(True)
        self.clear()
        for label, value in normalize_options(options):
            self.addItem(label, value)
        self.blockSignals(False)

    def value(self):
        """The selected value, or ``None``."""
        return self.currentData() if self.currentIndex() >= 0 else None

    def set_value(self, value) -> None:
        """Select by value. Raises ``ValueError`` if the value is not an option."""
        for index in range(self.count()):
            if self.itemData(index) == value:
                self.setCurrentIndex(index)
                return
        raise ValueError(f"{value!r} is not an option of this {type(self).__name__}.")

    def _emit_value(self, _index: int) -> None:
        self.value_changed.emit(self.value())


class ComboBox(Select):
    """An editable :class:`Select` with type-ahead; free text is allowed.

    Signals:
        value_changed(object): The selected value, or the free text entered.
    """

    _EDITABLE = True

    def __init__(self, options=None, parent=None, *, placeholder: str = "", **kwargs) -> None:
        super().__init__(options, parent, **kwargs)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        completer = self.completer() or QCompleter(self)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(completer)
        self.lineEdit().setPlaceholderText(placeholder)
        if "value" not in kwargs:
            self.setCurrentIndex(-1)
            self.lineEdit().clear()
        self.lineEdit().editingFinished.connect(self._on_edit)
        self._last = self.value()

    def value(self):
        text = self.currentText()
        index = self.findText(text)
        return self.itemData(index) if index >= 0 else (text or None)

    def _emit_value(self, _index: int) -> None:
        self._last = self.value()
        self.value_changed.emit(self._last)

    def _on_edit(self) -> None:
        if self.value() != self._last:
            self._last = self.value()
            self.value_changed.emit(self._last)


class _MultiPopup(PopupShell):
    def __init__(self, owner) -> None:
        super().__init__(owner)
        self.list = QListWidget()
        self.list.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.body.addWidget(self.list)


class MultiSelect(ThemedMixin, QPushButton):
    """Choose any number of values from a checkable popup list.

    Args:
        options: Entries, in the same forms as :class:`Select`.
        values: Initially selected values.
        placeholder: Text shown while nothing is selected.
        max_labels: Labels listed before the text collapses to a count.
        disabled: Start disabled.

    Signals:
        values_changed(list): The selected values, in option order.
    """

    values_changed = Signal(list)

    def __init__(self, options=None, parent=None, *, values=None, placeholder: str = "Select…", max_labels: int = 2,
                 disabled: bool = False) -> None:
        super().__init__(parent)
        self._placeholder, self._max_labels = placeholder, max_labels
        self._options = normalize_options(options)
        self._selected: list = list(values or [])
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(placeholder)
        self.popup = None
        self.setIconSize(QSize(14, 14))
        self.clicked.connect(self.show_popup)
        self.bind_theme()
        self._sync_text()
        self.setDisabled(disabled)

    def values(self) -> list:
        return [value for _, value in self._options if value in self._selected]

    def set_values(self, values) -> None:
        """Replace the selection and emit ``values_changed`` if it changed."""
        new = [value for _, value in self._options if value in list(values)]
        if new != self.values():
            self._selected = new
            self._sync_text()
            self._sync_list()
            self.values_changed.emit(new)

    def set_options(self, options) -> None:
        self._options = normalize_options(options)
        self._selected = self.values()
        self.popup = None
        self._sync_text()

    def show_popup(self) -> None:
        """Open the checkable list under the control."""
        if self.popup is None:
            self.popup = _MultiPopup(self)
            for label, value in self._options:
                item = QListWidgetItem(label)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setData(Qt.ItemDataRole.UserRole, value)
                self.popup.list.addItem(item)
            self._sync_list()
            self.popup.list.itemChanged.connect(self._on_item_changed)
            self.popup.list.itemClicked.connect(self._toggle_item)
        rows = min(8, max(1, len(self._options)))
        self.popup.resize(max(self.width(), 180) + 2 * PopupShell.MARGIN, rows * 30 + 12 + 2 * PopupShell.MARGIN)
        self.popup.show_at(self)
        self.popup.list.setFocus()

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().paintEvent(event)
        painter = QPainter(self)
        role = "text-disabled" if not self.isEnabled() else "text-tertiary"
        painter.drawPixmap(self.width() - 22, (self.height() - 14) // 2, icon_pixmap("chevron-down", 14, role))
        painter.end()

    def _toggle_item(self, item) -> None:
        checked = item.checkState() == Qt.CheckState.Checked
        item.setCheckState(Qt.CheckState.Unchecked if checked else Qt.CheckState.Checked)

    def _on_item_changed(self, _item) -> None:
        values = [
            self.popup.list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.popup.list.count())
            if self.popup.list.item(i).checkState() == Qt.CheckState.Checked
        ]
        if values != self.values():
            self._selected = values
            self._sync_text()
            self.values_changed.emit(self.values())

    def _sync_list(self) -> None:
        if not self.popup:
            return
        widget = self.popup.list
        widget.blockSignals(True)
        for index in range(widget.count()):
            item = widget.item(index)
            on = item.data(Qt.ItemDataRole.UserRole) in self._selected
            item.setCheckState(Qt.CheckState.Checked if on else Qt.CheckState.Unchecked)
        widget.blockSignals(False)

    def _sync_text(self) -> None:
        labels = [label for label, value in self._options if value in self._selected]
        if not labels:
            text = self._placeholder
        elif len(labels) <= self._max_labels:
            text = ", ".join(labels)
        else:
            text = f"{len(labels)} selected"
        self.setText(text)
        set_style_prop(self, "empty", "true" if not labels else "false")
