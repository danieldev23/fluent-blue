"""Small animation and elevation helpers driven by motion and elevation tokens."""
from __future__ import annotations

from ..compatibility.qt import QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QPropertyAnimation
from .theme_manager import ThemeManager


def animate(target, prop: bytes, end, *, start=None, duration: str = "normal", easing: str = "standard",
            on_finished=None) -> QPropertyAnimation | None:
    """Run a property animation using motion tokens.

    With animations disabled the end value is applied at once, the callback still
    runs, and ``None`` is returned. The animation is parented to ``target``, which
    keeps it alive, and deletes itself when finished.
    """
    ms = ThemeManager.duration(duration)
    if ms <= 0:
        target.setProperty(prop.decode(), end)
        if on_finished:
            on_finished()
        return None
    anim = QPropertyAnimation(target, prop, target)
    anim.setDuration(ms)
    anim.setEasingCurve(ThemeManager.easing(easing))
    if start is not None:
        anim.setStartValue(start)
    anim.setEndValue(end)
    if on_finished:
        anim.finished.connect(on_finished)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def fade(widget, start: float, end: float, *, duration: str = "normal", on_finished=None):
    """Fade a widget with a temporary opacity effect, removed afterwards to save repaints."""
    effect = QGraphicsOpacityEffect(widget)
    effect.setOpacity(start)
    widget.setGraphicsEffect(effect)

    def finished() -> None:
        widget.setGraphicsEffect(None)
        if on_finished:
            on_finished()

    return animate(effect, b"opacity", end, start=start, duration=duration, on_finished=finished)


def apply_elevation(widget, level: int) -> None:
    """Flat design mode: disables drop shadows to keep rendering crisp and minimal."""
    if isinstance(widget.graphicsEffect(), QGraphicsDropShadowEffect):
        widget.setGraphicsEffect(None)
