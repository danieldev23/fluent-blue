"""Shared helpers for all components."""
from __future__ import annotations

from ..compatibility.qt import QApplication, QPainter, QPen, QPixmap, QRectF, Qt
from ..core.theme_manager import ThemeManager


class ThemedMixin:
    """Hooks a component into the theme engine. Override :meth:`refresh_theme` for cached assets."""

    def bind_theme(self) -> None:
        ThemeManager.ensure_applied()
        ThemeManager.theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, _name: str = "") -> None:
        # Hidden widgets wait until they are shown: most never reappear before the next switch.
        if self.isVisible():
            self.refresh_theme()
            self.update()
        else:
            self._theme_stale = True

    def showEvent(self, event) -> None:  # noqa: N802 - Qt override
        if getattr(self, "_theme_stale", False):
            self._theme_stale = False
            self.refresh_theme()
        super().showEvent(event)

    def refresh_theme(self) -> None:
        """Rebuild anything derived from theme tokens that is not read at paint time."""


def repolish(widget) -> None:
    """Re-evaluate stylesheet rules after a dynamic property change, for this widget only."""
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def set_style_prop(widget, name: str, value) -> None:
    """Set a property used by stylesheet selectors, repolishing only if it changed."""
    if widget.property(name) != value:
        widget.setProperty(name, value)
        if widget.isVisible() or widget.testAttribute(Qt.WidgetAttribute.WA_WState_Polished):
            repolish(widget)


def check_choice(name: str, value, allowed) -> None:
    """Raise a clear ``ValueError`` for an unsupported option."""
    if value not in allowed:
        raise ValueError(f"Invalid {name} {value!r}. Expected one of: {', '.join(map(str, allowed))}.")


def apply_common(widget, *, disabled: bool = False, tooltip: str | None = None, accessible_name: str | None = None) -> None:
    """Apply the arguments shared by most components."""
    if disabled:
        widget.setDisabled(True)
    if tooltip:
        widget.setToolTip(tooltip)
    if accessible_name:
        widget.setAccessibleName(accessible_name)


def normalize_options(options) -> list[tuple[str, object]]:
    """Accept ``["a", ("Label", value), {"label": ..., "value": ...}]`` as ``(label, value)`` pairs."""
    result = []
    for option in options or []:
        if isinstance(option, dict):
            result.append((str(option["label"]), option.get("value", option["label"])))
        elif isinstance(option, (tuple, list)):
            result.append((str(option[0]), option[1]))
        else:
            result.append((str(option), option))
    return result


def device_ratio() -> float:
    app = QApplication.instance()
    screen = app.primaryScreen() if app else None
    return screen.devicePixelRatio() if screen else 1.0


def spinner_pixmap(size: int, color: str, angle: float, width: float = 2.0) -> QPixmap:
    """Draw one frame of the loading spinner: a faint ring with a 90 degree arc."""
    ratio = device_ratio()
    pixmap = QPixmap(round(size * ratio), round(size * ratio))
    pixmap.setDevicePixelRatio(ratio)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    paint_spinner(painter, QRectF(0, 0, size, size), color, angle, width)
    painter.end()
    return pixmap


def paint_spinner(painter: QPainter, rect: QRectF, color: str, angle: float, width: float = 2.0) -> None:
    """Paint a spinner into ``rect``. ``color`` is a role or hex value."""
    inset = width / 2 + .5
    area = rect.adjusted(inset, inset, -inset, -inset)
    faint = QPen(ThemeManager.qcolor(color, .22), width)
    painter.setPen(faint)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(area)
    pen = QPen(ThemeManager.qcolor(color), width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.drawArc(area, int(-angle * 16), 90 * 16)


def fit_wrapped_labels(widget) -> None:
    """Give wrapped labels inside ``widget`` the height their text needs at their current width.

    Nested layouts can under-estimate a wrapped label's height by one line, which clips the
    last line on some fonts. Call this from ``resizeEvent``; the value only changes when the
    width does, so it settles after one extra layout pass.
    """
    from ..compatibility.qt import QLabel

    for label in widget.findChildren(QLabel):
        if label.wordWrap() and label.text() and label.width() > 0:
            needed = label.heightForWidth(label.width())
            if needed > 0 and needed != label.minimumHeight():
                label.setMinimumHeight(needed)
