"""Convert typography tokens into ``QFont`` objects."""
from __future__ import annotations

from functools import lru_cache

from ..compatibility.qt import QFont, QFontDatabase, QGuiApplication
from .configuration import config
from .tokens import FONT_FAMILIES, MONO_FAMILIES, TYPOGRAPHY, TypeStyle

_WEIGHTS = {
    400: QFont.Weight.Normal, 500: QFont.Weight.Medium, 600: QFont.Weight.DemiBold,
    650: QFont.Weight.DemiBold, 700: QFont.Weight.Bold,
}


def scaled(size: float) -> int:
    """Apply the global font scale to a pixel size."""
    return max(1, round(size * config.font_scale))


@lru_cache(maxsize=1)
def _installed_families() -> frozenset:
    return frozenset(QFontDatabase.families())


def _available(families) -> list[str]:
    # Naming a missing family makes Qt build its alias table, a slow startup step, so
    # drop families this system lacks. The first installed preference wins.
    if QGuiApplication.instance() is None:
        return list(families)
    installed = _installed_families()
    usable = [name for name in families if name in installed or name.startswith(".")]
    return usable or list(families)


def make_font(style: str | TypeStyle = "body-medium", *, families=FONT_FAMILIES, mono_families=MONO_FAMILIES) -> QFont:
    """Build a ``QFont`` from a typography role name or a ``TypeStyle``."""
    spec = TYPOGRAPHY[style] if isinstance(style, str) else style
    font = QFont()
    font.setFamilies(_available(mono_families if spec.mono else families))
    font.setPixelSize(scaled(spec.size))
    font.setWeight(_WEIGHTS.get(spec.weight, QFont.Weight.Normal))
    if spec.tracking:
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spec.tracking)
    if spec.mono:
        font.setStyleHint(QFont.StyleHint.Monospace)
    else:
        font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return font
