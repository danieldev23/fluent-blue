"""Process-wide settings that apply across every theme."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Configuration:
    """Global behavior switches.

    Attributes:
        font_scale: Multiplier for all type sizes, for scalable typography.
        animations: Set ``False`` for reduced motion; animations jump to their end state.
        use_fusion_style: Use Qt's Fusion style, which gives stylesheets identical
            metrics on every platform. Native styles ignore parts of the stylesheet.
        apply_app_font: Set the themed font as the application font.
    """

    font_scale: float = 1.0
    animations: bool = True
    use_fusion_style: bool = True
    apply_app_font: bool = True


config = Configuration()
