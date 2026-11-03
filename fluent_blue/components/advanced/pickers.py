"""ColorPicker and FilePicker."""
from __future__ import annotations

from pathlib import Path

from ...compatibility.qt import (
    QColor,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QIcon,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QPointF,
    QRectF,
    QSize,
    QSizePolicy,
    Qt,
    QToolButton,
    QWidget,
    Signal,
)
from ...core.palette import parse_hex
from ...core.theme_manager import ThemeManager
from ..base import check_choice, device_ratio
from ..buttons.button import Button
from ..inputs.input import Input
from ..popup import PopupShell

_DEFAULT_PRESETS = ("primary-500", "primary-300", "primary-800", "success", "warning", "error", "info", "gray-500", "gray-900")


class _SaturationValue(QWidget):
    changed = Signal(float, float)

    def __init__(self) -> None:
        super().__init__()
        self.hue, self.sat, self.val = 0.0, 1.0, 1.0
        self.setFixedHeight(150)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        horizontal = QLinearGradient(0, 0, rect.width(), 0)
        horizontal.setColorAt(0, QColor(Qt.GlobalColor.white))
        horizontal.setColorAt(1, QColor.fromHsvF(self.hue, 1, 1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(horizontal)
        painter.drawRoundedRect(rect, 6, 6)
        vertical = QLinearGradient(0, 0, 0, rect.height())
        vertical.setColorAt(0, QColor(0, 0, 0, 0))
        vertical.setColorAt(1, QColor(Qt.GlobalColor.black))
        painter.setBrush(vertical)
        painter.drawRoundedRect(rect, 6, 6)
        point = QPointF(self.sat * rect.width(), (1 - self.val) * rect.height())
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(Qt.GlobalColor.white), 2))
        painter.drawEllipse(point, 6, 6)
        painter.setPen(QPen(QColor(0, 0, 0, 90), 1))
        painter.drawEllipse(point, 7.5, 7.5)
        painter.end()

    def _pick(self, pos) -> None:
        self.sat = min(1.0, max(0.0, pos.x() / max(1, self.width())))
        self.val = 1 - min(1.0, max(0.0, pos.y() / max(1, self.height())))
        self.update()
        self.changed.emit(self.sat, self.val)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        self._pick(event.position())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        self._pick(event.position())


class _HueBar(QWidget):
    changed = Signal(float)

    def __init__(self) -> None:
        super().__init__()
        self.hue = 0.0
        self.setFixedHeight(14)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName("Hue")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        for step in range(7):
            gradient.setColorAt(step / 6, QColor.fromHsvF(min(step / 6, .999), 1, 1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(QRectF(self.rect()), 7, 7)
        x = 7 + self.hue * (self.width() - 14)
        painter.setPen(QPen(ThemeManager.qcolor("border-focus") if self.hasFocus() else QColor(0, 0, 0, 90), 2 if self.hasFocus() else 1))
        painter.setBrush(QColor(Qt.GlobalColor.white))
        painter.drawEllipse(QPointF(x, 7), 6, 6)
        painter.end()

    def _pick(self, pos) -> None:
        self.hue = min(.999, max(0.0, (pos.x() - 7) / max(1, self.width() - 14)))
        self.update()
        self.changed.emit(self.hue)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        self._pick(event.position())

    def mouseMoveEvent(self, event) -> None:  # noqa: N802 - Qt override
        self._pick(event.position())

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            delta = -.01 if event.key() == Qt.Key.Key_Left else .01
            self.hue = min(.999, max(0.0, self.hue + delta))
            self.update()
            self.changed.emit(self.hue)
        else:
            super().keyPressEvent(event)


def _swatch(color: str, size: int) -> QPixmap:
    ratio = device_ratio()
    pixmap = QPixmap(round(size * ratio), round(size * ratio))
    pixmap.setDevicePixelRatio(ratio)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(ThemeManager.qcolor("border-strong"), 1))
    painter.setBrush(QColor(color))
    painter.drawRoundedRect(QRectF(.5, .5, size - 1, size - 1), 3, 3)
    painter.end()
    return pixmap


class ColorPicker(Button):
    """A swatch button that opens a saturation/value square, hue bar, hex field and presets.

    Args:
        color: Initial color as ``#RRGGBB``.
        presets: Hex values or color roles offered as shortcuts.

    Signals:
        color_changed(str): The new color as uppercase ``#RRGGBB``.
    """

    color_changed = Signal(str)

    def __init__(self, parent=None, *, color: str = "#1677FF", presets=_DEFAULT_PRESETS, **kwargs) -> None:
        self._color = color.upper()
        self._presets = tuple(presets)
        self.popup = None
        super().__init__(self._color, parent, variant=kwargs.pop("variant", "secondary"), **kwargs)
        self.setIconSize(QSize(16, 16))
        self.setAccessibleName(f"Color {self._color}")
        self.clicked.connect(self.open_popup)
        self._sync_button()

    def color(self) -> str:
        return self._color

    def set_color(self, color: str) -> None:
        """Set the color and emit ``color_changed`` if it changed."""
        parse_hex(color)
        color = color.upper()[:7]
        if color != self._color:
            self._color = color
            self._sync_button()
            self._sync_popup()
            self.color_changed.emit(color)

    def refresh_theme(self) -> None:
        self._sync_button()

    def _update_icon(self) -> None:
        self._sync_button()

    def _sync_button(self) -> None:
        self.setText(self._color)
        self.setIcon(QIcon(_swatch(self._color, 16)))
        self.setAccessibleName(f"Color {self._color}")

    def open_popup(self) -> None:
        """Open the picker popup."""
        if self.popup is None:
            self._build_popup()
        self._sync_popup()
        self.popup.adjustSize()
        self.popup.show_at(self)
        self.hue_bar.setFocus()

    def _build_popup(self) -> None:
        popup = PopupShell(self, padding=10)
        popup.setFixedWidth(232 + 2 * PopupShell.MARGIN)
        popup.body.setSpacing(10)
        self.sv = _SaturationValue()
        self.hue_bar = _HueBar()
        self.hex_input = Input(size="small", prefix_icon="droplet", accessible_name="Hex color")
        self.sv.changed.connect(lambda _s, _v: self._from_hsv())
        self.hue_bar.changed.connect(lambda _h: self._from_hsv())
        self.hex_input.editingFinished.connect(self._from_hex)
        popup.body.addWidget(self.sv)
        popup.body.addWidget(self.hue_bar)
        popup.body.addWidget(self.hex_input)
        grid = QGridLayout()
        grid.setSpacing(4)
        for index, preset in enumerate(self._presets):
            value = preset if preset.startswith("#") else ThemeManager.color(preset)
            button = QToolButton()
            button.setIcon(QIcon(_swatch(value, 20)))
            button.setIconSize(QSize(20, 20))
            button.setAutoRaise(True)
            button.setAccessibleName(f"Preset {value}")
            button.clicked.connect(lambda _=False, v=value: self.set_color(v))
            grid.addWidget(button, index // 9, index % 9)
        popup.body.addLayout(grid)
        self.popup = popup

    def _sync_popup(self) -> None:
        if not self.popup:
            return
        hue, sat, val, _ = QColor(self._color).getHsvF()
        self.hue_bar.hue = max(0.0, hue)
        self.sv.hue, self.sv.sat, self.sv.val = max(0.0, hue), sat, val
        self.hex_input.setText(self._color)
        self.sv.update()
        self.hue_bar.update()

    def _from_hsv(self) -> None:
        self.sv.hue = self.hue_bar.hue
        color = QColor.fromHsvF(self.hue_bar.hue, self.sv.sat, self.sv.val).name().upper()
        self.sv.update()
        if color != self._color:
            self._color = color
            self._sync_button()
            self.hex_input.setText(color)
            self.color_changed.emit(color)

    def _from_hex(self) -> None:
        text = self.hex_input.text().strip()
        text = text if text.startswith("#") else f"#{text}"
        try:
            self.set_color(text)
            self.hex_input.set_validation("none")
        except ValueError:
            self.hex_input.set_validation("error")


class FilePicker(QWidget):
    """A path field with a browse button and drag and drop.

    Args:
        mode: ``open``, ``open-multiple``, ``save`` or ``directory``.
        filter: Qt name filter, such as ``"Images (*.png *.jpg)"``.
        placeholder: Placeholder text.
        button_text: Label of the browse button.
        disabled: Start disabled.

    Signals:
        file_selected(str): A path was chosen, the first one in multiple mode.
        files_selected(list): All chosen paths.
    """

    file_selected = Signal(str)
    files_selected = Signal(list)

    def __init__(self, parent=None, *, mode: str = "open", filter: str = "", placeholder: str = "No file selected",  # noqa: A002
                 button_text: str = "Browse…", disabled: bool = False) -> None:
        super().__init__(parent)
        check_choice("mode", mode, ("open", "open-multiple", "save", "directory"))
        self._mode, self._filter = mode, filter
        self._paths: list[str] = []
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        icon = "folder" if mode == "directory" else "file"
        self.input = Input(placeholder=placeholder, prefix_icon=icon, read_only=True)
        self.button = Button(button_text)
        self.button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.button.clicked.connect(self.browse)
        layout.addWidget(self.input, 1)
        layout.addWidget(self.button)
        self.setDisabled(disabled)

    def path(self) -> str:
        return self._paths[0] if self._paths else ""

    def paths(self) -> list[str]:
        return list(self._paths)

    def set_paths(self, paths) -> None:
        """Set the selection and emit the signals."""
        self._paths = [str(p) for p in paths]
        if len(self._paths) > 1:
            self.input.setText(f"{len(self._paths)} files selected")
        else:
            self.input.setText(self.path())
        if self._paths:
            self.file_selected.emit(self._paths[0])
        self.files_selected.emit(self.paths())

    def browse(self) -> None:
        """Open the native file dialog."""
        start = self.path()
        if self._mode == "open":
            path, _ = QFileDialog.getOpenFileName(self, "Open file", start, self._filter)
            paths = [path] if path else []
        elif self._mode == "open-multiple":
            paths, _ = QFileDialog.getOpenFileNames(self, "Open files", start, self._filter)
        elif self._mode == "save":
            path, _ = QFileDialog.getSaveFileName(self, "Save file", start, self._filter)
            paths = [path] if path else []
        else:
            path = QFileDialog.getExistingDirectory(self, "Choose folder", start)
            paths = [path] if path else []
        if paths:
            self.set_paths(paths)

    def dragEnterEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.mimeData().hasUrls() and self._accepts(self._dropped(event)):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:  # noqa: N802 - Qt override
        paths = self._dropped(event)
        if self._accepts(paths):
            self.set_paths(paths if self._mode == "open-multiple" else paths[:1])
            event.acceptProposedAction()

    @staticmethod
    def _dropped(event) -> list[str]:
        return [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]

    def _accepts(self, paths: list[str]) -> bool:
        if not paths or self._mode == "save":
            return False
        return all(Path(p).is_dir() == (self._mode == "directory") for p in paths)

