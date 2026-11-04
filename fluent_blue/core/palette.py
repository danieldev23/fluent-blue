"""Semantic color roles for each base theme, plus pure color math. No Qt dependency."""
from __future__ import annotations

import colorsys
import re
from functools import lru_cache

from .tokens import ANT_PRESET_COLORS, GRAY_RAMP, PRIMARY_RAMP

_HEX = re.compile(r"^#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


@lru_cache(maxsize=1024)
def parse_hex(value: str) -> tuple[int, int, int, int]:
    """Parse ``#RRGGBB`` or ``#RRGGBBAA`` into an RGBA tuple."""
    if not _HEX.match(value):
        raise ValueError(f"Invalid color {value!r}; expected #RRGGBB or #RRGGBBAA.")
    digits = value[1:]
    r, g, b = int(digits[:2], 16), int(digits[2:4], 16), int(digits[4:6], 16)
    return r, g, b, int(digits[6:8], 16) if len(digits) == 8 else 255


def to_hex(r: float, g: float, b: float, a: float = 255) -> str:
    text = f"#{round(r):02X}{round(g):02X}{round(b):02X}"
    return text if round(a) == 255 else f"{text}{round(a):02X}"


def mix(first: str, second: str, amount: float) -> str:
    """Blend ``second`` into ``first``; ``amount`` 0 gives first, 1 gives second."""
    a, b = parse_hex(first), parse_hex(second)
    return to_hex(*(x + (y - x) * amount for x, y in zip(a, b)))


def with_alpha(color: str, alpha: float) -> str:
    r, g, b, _ = parse_hex(color)
    return to_hex(r, g, b, 255 * alpha)


def luminance(color: str) -> float:
    """WCAG relative luminance, ignoring alpha."""
    def channel(value: int) -> float:
        s = value / 255
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4
    r, g, b, _ = parse_hex(color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(first: str, second: str) -> float:
    """WCAG 2.1 contrast ratio between two opaque colors."""
    a, b = sorted((luminance(first), luminance(second)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def readable_on(background: str, light: str = "#FFFFFF", dark: str = "#141414") -> str:
    """Pick whichever of ``light`` / ``dark`` has more contrast on ``background``."""
    return light if contrast_ratio(background, light) >= contrast_ratio(background, dark) else dark


def derive_ramp(base: str) -> dict[str, str]:
    """Build a 10-step ramp around ``base`` with a lightness and saturation curve tuned for UI surfaces."""
    base_hex = base.lstrip("#")
    r, g, b = [int(base_hex[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h_deg = round(h * 360)

    hue_step = 2
    sat_step = 0.16
    sat_step2 = 0.05
    bright_step1 = 0.05
    bright_step2 = 0.15
    light_count = 5
    dark_count = 4

    def get_hue(i, light):
        if 60 <= h_deg <= 240:
            hue = h_deg - hue_step * i if light else h_deg + hue_step * i
        else:
            hue = h_deg + hue_step * i if light else h_deg - hue_step * i
        return (hue % 360) / 360.0

    def get_sat(i, light):
        if h_deg == 0 and s == 0:
            return s
        if light:
            sat = s - sat_step * i
        elif i == dark_count:
            sat = s + sat_step
        else:
            sat = s + sat_step2 * i
        sat = min(1.0, max(0.06, sat))
        if light and i == light_count and sat > 0.1:
            sat = 0.1
        return round(sat, 2)

    def get_val(i, light):
        val = v + bright_step1 * i if light else v - bright_step2 * i
        return round(max(0.0, min(1.0, val)), 2)

    keys = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
    shades = []
    for i in range(light_count, 0, -1):
        nh = get_hue(i, True)
        ns = get_sat(i, True)
        nv = get_val(i, True)
        nr, ng, nb = colorsys.hsv_to_rgb(nh, ns, nv)
        shades.append(to_hex(nr * 255, ng * 255, nb * 255))
    shades.append(to_hex(r * 255, g * 255, b * 255))
    for i in range(1, dark_count + 1):
        nh = get_hue(i, False)
        ns = get_sat(i, False)
        nv = get_val(i, False)
        nr, ng, nb = colorsys.hsv_to_rgb(nh, ns, nv)
        shades.append(to_hex(nr * 255, ng * 255, nb * 255))

    return dict(zip(keys, shades))


# Text and fills for content placed on the brand gradient, in every theme.
_BRAND_RAIL = {
    "brand-text": "#FFFFFF", "brand-text-muted": "#EEF6FF", "brand-fill-hover": "#001D6640",
    "brand-fill-active": "#001D6680", "brand-border": "#FFFFFF40",
}


def _base_roles() -> dict[str, str]:
    colors = {f"primary-{k}": v for k, v in PRIMARY_RAMP.items()}
    colors.update({f"gray-{k}": v for k, v in GRAY_RAMP.items()})
    for p_name, p_shades in ANT_PRESET_COLORS.items():
        for idx, shade in enumerate(p_shades, start=1):
            colors[f"{p_name}-{idx}"] = shade
            colors[f"ant-{p_name}-{idx}"] = shade
    return colors


def _semantic_light(colors: dict[str, str], name: str, base: str) -> None:
    colors[name] = base
    colors[f"{name}-hover"] = mix(base, "#000000", .10)
    colors[f"{name}-pressed"] = mix(base, "#000000", .20)
    colors[f"{name}-subtle"] = mix(base, "#FFFFFF", .91)
    colors[f"{name}-border"] = mix(base, "#FFFFFF", .68)
    colors[f"{name}-text"] = base
    colors[f"on-{name}"] = "#FFFFFF"


def _semantic_dark(colors: dict[str, str], name: str, base: str) -> None:
    colors[name] = base
    colors[f"{name}-hover"] = mix(base, "#FFFFFF", .10)
    colors[f"{name}-pressed"] = mix(base, "#000000", .12)
    colors[f"{name}-subtle"] = mix(base, colors["surface"], .82)
    colors[f"{name}-border"] = mix(base, colors["surface"], .50)
    colors[f"{name}-text"] = base
    colors[f"on-{name}"] = "#FFFFFF"


# Roles that carry or sit behind text. They are applied last in each theme so that every
# text pairing meets WCAG AA (4.5:1). The ramps keep their brand values; tests enforce this.
_ACCESSIBLE_LIGHT = {
    "text-tertiary": "#555555",
    "primary": "#0E68EA", "primary-hover": "#0958D9", "primary-pressed": "#0848B8", "primary-text": "#0958D9",
    "brand-gradient-start": "#0E68EA", "brand-gradient-end": "#0F63DF",
    "success-text": "#237804", "warning-text": "#9A5C00", "error-text": "#CF1322", "info-text": "#0958D9",
    "error": "#D92D30", "error-hover": "#C4262A", "error-pressed": "#A81E22",
}
_ACCESSIBLE_DARK = {
    "text-tertiary": "#A6A6A6",
    "primary": "#1668DC", "primary-hover": "#1A6DE4", "primary-pressed": "#1554AD", "primary-text": "#69B1FF",
    "border-focus": "#4096FF", "brand-gradient-start": "#1668DC", "brand-gradient-end": "#1F6BD6",
    "success-text": "#73D13D", "warning-text": "#FFC53D", "error-text": "#FF7875", "info-text": "#69B1FF",
    "error": "#C93538", "error-hover": "#D13D40", "error-pressed": "#A82B2E",
}
_ACCESSIBLE_HIGH_CONTRAST = {
    "primary-hover": "#1466FF", "error": "#C93538", "error-hover": "#D13D40", "error-pressed": "#A82B2E",
    "error-text": "#FF9C9C", "info-text": "#9CC2FF", "success-text": "#95DE64", "warning-text": "#FFD666",
}


def light_colors() -> dict[str, str]:
    """Semantic roles of the Fluent Blue Light theme."""
    c = _base_roles()
    c.update({
        "background": "#F5F5F5", "surface": "#FFFFFF", "surface-secondary": "#FAFAFA",
        "surface-tertiary": "#F0F0F0", "surface-elevated": "#FFFFFF", "surface-overlay": "#00000073",
        "text-primary": "#141414", "text-secondary": "#595959", "text-tertiary": "#8C8C8C",
        "text-disabled": "#BFBFBF", "text-inverse": "#FFFFFF",
        "border": "#D9D9D9", "border-subtle": "#F0F0F0", "border-strong": "#BFBFBF",
        "border-focus": "#1677FF",
        "primary": "#1677FF", "primary-hover": "#4096FF",
        "primary-pressed": "#0958D9", "primary-subtle": "#E6F4FF",
        "primary-subtle-hover": "#BAE0FF", "primary-border": "#91CAFF",
        "primary-text": "#1677FF", "on-primary": "#FFFFFF",
        "control": "#FFFFFF", "control-hover": "#FAFAFA", "control-pressed": "#F0F0F0",
        "control-disabled": "#F5F5F5", "ghost-hover": "#F5F5F5", "ghost-pressed": "#E8E8E8",
        "selection": "#E6F4FF", "selection-text": "#0958D9",
        "scrollbar": "#BFBFBF", "scrollbar-hover": "#8C8C8C",
        "shadow": "#000000", "brand-gradient-start": "#1677FF", "brand-gradient-end": "#69B1FF",
        **_BRAND_RAIL,
    })
    c.update({
        "success": "#52C41A", "success-hover": "#73D13D", "success-pressed": "#389E0D",
        "success-subtle": "#F6FFED", "success-border": "#B7EB8F", "success-text": "#52C41A",
        "on-success": "#FFFFFF",
        "warning": "#FAAD14", "warning-hover": "#FFC53D", "warning-pressed": "#D48806",
        "warning-subtle": "#FFFBE6", "warning-border": "#FFE58F", "warning-text": "#FAAD14",
        "on-warning": "#FFFFFF",
        "error": "#FF4D4F", "error-hover": "#FF7875", "error-pressed": "#D9363E",
        "error-subtle": "#FFF2F0", "error-border": "#FFCCC7", "error-text": "#FF4D4F",
        "on-error": "#FFFFFF",
        "info": "#1677FF", "info-hover": "#4096FF", "info-pressed": "#0958D9",
        "info-subtle": "#E6F4FF", "info-border": "#91CAFF", "info-text": "#1677FF",
        "on-info": "#FFFFFF",
    })
    c.update(_ACCESSIBLE_LIGHT)
    c["surface-primary"] = c["surface"]
    return c


def dark_colors() -> dict[str, str]:
    """Semantic roles of the Fluent Blue Dark theme."""
    c = _base_roles()
    c.update({
        "background": "#000000", "surface": "#141414", "surface-secondary": "#1F1F1F",
        "surface-tertiary": "#262626", "surface-elevated": "#1F1F1F", "surface-overlay": "#000000A6",
        "text-primary": "#E6E6E6", "text-secondary": "#A6A6A6", "text-tertiary": "#737373",
        "text-disabled": "#404040", "text-inverse": "#141414",
        "border": "#424242", "border-subtle": "#303030", "border-strong": "#5A5A5A",
        "border-focus": "#1668DC",
        "primary": "#1668DC", "primary-hover": "#3C89E8",
        "primary-pressed": "#1554AD", "primary-subtle": "#111A2C",
        "primary-subtle-hover": "#15325B", "primary-border": "#15325B",
        "primary-text": "#3C89E8", "on-primary": "#FFFFFF",
        "control": "#141414", "control-hover": "#1F1F1F", "control-pressed": "#262626",
        "control-disabled": "#1F1F1F", "ghost-hover": "#1F1F1F", "ghost-pressed": "#262626",
        "selection": "#15325B", "selection-text": "#BAE0FF",
        "scrollbar": "#303030", "scrollbar-hover": "#424242",
        "shadow": "#000000", "brand-gradient-start": "#1668DC", "brand-gradient-end": "#3C89E8",
        **_BRAND_RAIL,
    })
    c.update({
        "success": "#49AA19", "success-hover": "#6ABE39", "success-pressed": "#3C8618",
        "success-subtle": "#162312", "success-border": "#274916", "success-text": "#49AA19",
        "on-success": "#FFFFFF",
        "warning": "#D89614", "warning-hover": "#E8B339", "warning-pressed": "#AA7714",
        "warning-subtle": "#2B2111", "warning-border": "#594214", "warning-text": "#D89614",
        "on-warning": "#FFFFFF",
        "error": "#DC4446", "error-hover": "#E86E6B", "error-pressed": "#AD393A",
        "error-subtle": "#2C1618", "error-border": "#5B2526", "error-text": "#DC4446",
        "on-error": "#FFFFFF",
        "info": "#1668DC", "info-hover": "#3C89E8", "info-pressed": "#1554AD",
        "info-subtle": "#111A2C", "info-border": "#15325B", "info-text": "#1668DC",
        "on-info": "#FFFFFF",
    })
    c.update(_ACCESSIBLE_DARK)
    c["surface-primary"] = c["surface"]
    return c


def high_contrast_colors() -> dict[str, str]:
    """An accessibility theme: pure black surfaces and at least 7:1 body text."""
    c = dark_colors()
    c.update({
        "background": "#000000", "surface": "#000000", "surface-secondary": "#0A0A0A",
        "surface-tertiary": "#141414", "surface-elevated": "#0A0A0A",
        "text-primary": "#FFFFFF", "text-secondary": "#F0F0F0", "text-tertiary": "#D8D8D8",
        "text-disabled": "#9A9A9A", "border": "#FFFFFF", "border-subtle": "#BDBDBD",
        "border-strong": "#FFFFFF", "border-focus": "#FFD400",
        "primary": "#0B5CFF", "primary-hover": "#2A72FF", "primary-pressed": "#0848C9", "primary-text": "#9CC2FF",
        "control": "#000000", "control-hover": "#1F1F1F", "control-pressed": "#303030",
        "control-disabled": "#0A0A0A", "ghost-hover": "#1F1F1F", "ghost-pressed": "#303030",
        "selection": "#FFD400", "selection-text": "#000000",
    })
    c.update(_ACCESSIBLE_HIGH_CONTRAST)
    c["surface-primary"] = c["surface"]
    return c


def normalize_overrides(overrides: dict[str, str] | None) -> dict[str, str]:
    """Accept ``text_primary`` as well as ``text-primary`` and validate each value."""
    result = {}
    for key, value in (overrides or {}).items():
        parse_hex(value)
        result[key.replace("_", "-")] = value.upper()
    return result


def apply_overrides(colors: dict[str, str], overrides: dict[str, str] | None, is_dark: bool) -> dict[str, str]:
    """Merge overrides into ``colors``.

    Overriding ``primary`` alone regenerates the ramp and every interactive primary
    role, so a custom brand color needs a single line. Any role named explicitly in
    ``overrides`` still wins over the derived value.
    """
    result = dict(colors)
    custom = normalize_overrides(overrides)
    if "primary" in custom:
        base = custom["primary"]
        ramp = derive_ramp(base)
        result.update({f"primary-{k}": v for k, v in ramp.items()})
        surface = custom.get("surface", result["surface"])
        result.update({
            "primary": base,
            "primary-hover": ramp["600"] if not is_dark else mix(base, "#FFFFFF", .06),
            "primary-pressed": ramp["600"] if not is_dark else ramp["700"],
            "primary-subtle": mix(base, surface, .82) if is_dark else ramp["50"],
            "primary-subtle-hover": mix(base, surface, .74) if is_dark else ramp["100"],
            "primary-border": mix(base, surface, .55) if is_dark else ramp["200"],
            "primary-text": ramp["300"] if is_dark else ramp["600"],
            "on-primary": readable_on(base),
            "border-focus": ramp["400"] if is_dark else base,
            "selection": mix(base, surface, .68) if is_dark else ramp["50"],
            "selection-text": "#FFFFFF" if is_dark else ramp["700"],
            "brand-gradient-start": base,
            "brand-gradient-end": ramp["300"],
        })
    result.update(custom)
    return result
