"""Theme-independent design tokens: primitive colors, spacing, radius, elevation, motion.

This module has no Qt dependency so that tokens can be inspected, documented and
tested without a display. Semantic color roles live in :mod:`fluent_blue.core.palette`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

PRIMARY_RAMP: dict[str, str] = {
    "50": "#E6F4FF",   # Ant Design blue-1
    "100": "#BAE0FF",  # Ant Design blue-2
    "200": "#91CAFF",  # Ant Design blue-3
    "300": "#69B1FF",  # Ant Design blue-4
    "400": "#4096FF",  # Ant Design blue-5 (hover)
    "500": "#1677FF",  # Ant Design blue-6 (primary base)
    "600": "#0958D9",  # Ant Design blue-7 (active/pressed)
    "700": "#003EB3",  # Ant Design blue-8
    "800": "#002C8C",  # Ant Design blue-9
    "900": "#001D66",  # Ant Design blue-10
}

GRAY_RAMP: dict[str, str] = {
    "0": "#FFFFFF",
    "50": "#FAFAFA",   # Ant Design colorFillAlter
    "100": "#F5F5F5",  # Ant Design colorBgLayout
    "200": "#F0F0F0",  # Ant Design colorBorderSecondary
    "300": "#D9D9D9",  # Ant Design colorBorder
    "400": "#BFBFBF",  # Ant Design colorTextDisabled
    "500": "#8C8C8C",  # Ant Design colorTextDescription
    "600": "#595959",  # Ant Design colorTextSecondary
    "700": "#434343",  # Ant Design text dark
    "800": "#262626",  # Ant Design text heading
    "900": "#1F1F1F",  # Ant Design elevated container
    "950": "#141414",  # Ant Design container base
    "1000": "#000000", # Pure black
}

SEMANTIC_BASE: dict[str, str] = {
    "success": "#52C41A",  # Ant Design Polar Green 6
    "warning": "#FAAD14",  # Ant Design Calendula Gold 6
    "error": "#FF4D4F",    # Ant Design Dust Red (colorError)
    "info": "#1677FF",     # Ant Design Daybreak Blue 6
}

# The 12 Ant Design preset color palettes (10 shades each)
ANT_PRESET_COLORS: dict[str, list[str]] = {
    "blue": ["#E6F4FF", "#BAE0FF", "#91CAFF", "#69B1FF", "#4096FF", "#1677FF", "#0958D9", "#003EB3", "#002C8C", "#001D66"],
    "purple": ["#F9F0FF", "#EFDBFF", "#D3ADF7", "#B37FEB", "#9254DE", "#722ED1", "#531DAB", "#391085", "#22075E", "#120338"],
    "cyan": ["#E6FFFB", "#B5F5EC", "#87E8DE", "#5CDBD3", "#36CFC9", "#13C2C2", "#08979C", "#006D75", "#00474F", "#002329"],
    "green": ["#F6FFED", "#D9F7BE", "#B7EB8F", "#95DE64", "#73D13D", "#52C41A", "#389E0D", "#237804", "#135200", "#092B00"],
    "magenta": ["#FFF0F6", "#FFD6E7", "#FFADD2", "#FF85C0", "#F759AB", "#EB2F96", "#C41D7F", "#9E1068", "#780650", "#520339"],
    "pink": ["#FFF0F6", "#FFD6E7", "#FFADD2", "#FF85C0", "#F759AB", "#EB2F96", "#C41D7F", "#9E1068", "#780650", "#520339"],
    "red": ["#FFF1F0", "#FFCCC7", "#FFA39E", "#FF7875", "#FF4D4F", "#F5222D", "#CF1322", "#A8071A", "#820014", "#5C0011"],
    "orange": ["#FFF7E6", "#FFE7BA", "#FFD591", "#FFC069", "#FFA940", "#FA8C16", "#D46B08", "#AD4E00", "#873800", "#612500"],
    "yellow": ["#FEFFE6", "#FFFFB8", "#FFFB8F", "#FFF566", "#FFEC3D", "#FADB14", "#D4B106", "#AD8B00", "#876800", "#614700"],
    "volcano": ["#FFF2E8", "#FFD8BF", "#FFBB96", "#FF9C6E", "#FF7A45", "#FA541C", "#D4380D", "#AD2102", "#871400", "#610B00"],
    "geekblue": ["#F0F5FF", "#D6E4FF", "#ADC6FF", "#85A5FF", "#597EF7", "#2F54EB", "#1D39C4", "#10239E", "#061178", "#030852"],
    "gold": ["#FFFBE6", "#FFF1B8", "#FFE58F", "#FFD666", "#FFC53D", "#FAAD14", "#D48806", "#AD6800", "#874D00", "#613400"],
    "lime": ["#FCFFE6", "#F4FFB8", "#EAFF8F", "#D3F261", "#BAE637", "#A0D911", "#7CB305", "#5B8C00", "#3F6600", "#254000"],
}

SPACING: dict[str, int] = {
    "0": 0, "1": 4, "2": 8, "3": 12, "4": 16, "5": 20, "6": 24,
    "8": 32, "10": 40, "12": 48, "16": 64, "20": 80,
}

RADIUS: dict[str, int] = {
    "none": 0, "xs": 2, "sm": 4, "md": 6, "lg": 8, "xl": 12, "full": 999,
}


@dataclass(frozen=True)
class Shadow:
    """A drop shadow. ``alpha`` is scaled by the theme's shadow strength."""

    offset_y: int
    blur: int
    alpha: float


ELEVATION: dict[int, Shadow] = {
    0: Shadow(0, 0, 0.0),
    1: Shadow(1, 6, 0.12),
    2: Shadow(3, 14, 0.16),
    3: Shadow(8, 26, 0.20),
    4: Shadow(14, 40, 0.26),
}

MOTION: dict[str, int | str] = {
    "duration-fast": 90,
    "duration-normal": 160,
    "duration-slow": 260,
    "easing-standard": "OutCubic",
    "easing-emphasized": "OutQuint",
}

# Height in pixels of interactive controls, by size name.
CONTROL_HEIGHT: dict[str, int] = {"small": 28, "medium": 34, "large": 40}
ICON_SIZE: dict[str, int] = {"xs": 12, "small": 14, "medium": 16, "large": 20, "xl": 24, "xxl": 40}


@dataclass(frozen=True)
class TypeStyle:
    """One typography role. ``size`` is unscaled pixels; ``tracking`` is in pixels."""

    size: int
    weight: int
    line_height: int
    tracking: float = 0.0
    mono: bool = False


TYPOGRAPHY: dict[str, TypeStyle] = {
    "display": TypeStyle(36, 700, 44, -0.6),
    "heading-1": TypeStyle(28, 700, 36, -0.4),
    "heading-2": TypeStyle(22, 650, 30, -0.25),
    "heading-3": TypeStyle(18, 600, 26, -0.1),
    "heading-4": TypeStyle(16, 600, 24),
    "heading-5": TypeStyle(14, 600, 20),
    "heading-6": TypeStyle(13, 600, 18),
    "body-large": TypeStyle(15, 400, 24),
    "body-medium": TypeStyle(13, 400, 20),
    "body-small": TypeStyle(12, 400, 18),
    "caption": TypeStyle(11, 400, 16, 0.1),
    "label": TypeStyle(12, 500, 16),
    "button": TypeStyle(13, 500, 16),
    "monospace": TypeStyle(12, 400, 18, 0.0, True),
}

FONT_FAMILIES: tuple[str, ...] = (
    ".AppleSystemUIFont", "Avenir Next", "Avenir",
    "Segoe UI", "Inter", "Helvetica Neue", "Cantarell", "sans-serif",
)
MONO_FAMILIES: tuple[str, ...] = (
    "SF Mono", "Menlo", "Cascadia Code", "Consolas", "JetBrains Mono",
    "DejaVu Sans Mono", "Courier New", "monospace",
)


@dataclass
class DesignTokens:
    """The configurable non-color tokens carried by a theme."""

    spacing: dict[str, int] = field(default_factory=lambda: dict(SPACING))
    radius: dict[str, int] = field(default_factory=lambda: dict(RADIUS))
    elevation: dict[int, Shadow] = field(default_factory=lambda: dict(ELEVATION))
    motion: dict[str, int | str] = field(default_factory=lambda: dict(MOTION))
    typography: dict[str, TypeStyle] = field(default_factory=lambda: dict(TYPOGRAPHY))
    control_height: dict[str, int] = field(default_factory=lambda: dict(CONTROL_HEIGHT))
    icon_size: dict[str, int] = field(default_factory=lambda: dict(ICON_SIZE))
    font_families: tuple[str, ...] = FONT_FAMILIES
    mono_families: tuple[str, ...] = MONO_FAMILIES

    def merged(self, overrides: dict | None) -> DesignTokens:
        """Return a copy with ``overrides`` applied; unknown groups raise ``KeyError``."""
        result = DesignTokens(
            dict(self.spacing), dict(self.radius), dict(self.elevation), dict(self.motion),
            dict(self.typography), dict(self.control_height), dict(self.icon_size),
            self.font_families, self.mono_families,
        )
        for group, values in (overrides or {}).items():
            if not hasattr(result, group):
                raise KeyError(f"Unknown token group: {group!r}")
            if isinstance(values, dict):
                target = getattr(result, group)
                for key, value in values.items():
                    if group == "typography" and isinstance(value, dict):
                        value = TypeStyle(**{**target[key].__dict__, **value})
                    elif group == "elevation" and isinstance(value, dict):
                        value = Shadow(**value)
                    target[key] = value
            else:
                setattr(result, group, tuple(values))
        return result
