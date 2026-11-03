"""Token access for stylesheet templates."""
from __future__ import annotations

from ...core.palette import parse_hex
from ...core.theme_manager import Theme
from ...core.typography import scaled
from ...icons.engine import qss_asset


class Colors:
    """Maps a role name to a QSS color. Attribute access uses underscores for hyphens."""

    def __init__(self, colors: dict[str, str]) -> None:
        self._colors = colors

    def __getitem__(self, role: str) -> str:
        value = self._colors[role]
        r, g, b, a = parse_hex(value)
        return value[:7] if a == 255 else f"rgba({r}, {g}, {b}, {a})"

    def __getattr__(self, name: str) -> str:
        return self[name.replace("_", "-")]


class Ctx:
    """Everything a stylesheet template needs from the active theme."""

    def __init__(self, theme: Theme) -> None:
        self.theme = theme
        self.c = Colors(theme.colors)
        self.t = theme.tokens

    def r(self, name: str) -> str:
        return f"{self.t.radius[name]}px"

    def s(self, step) -> str:
        return f"{self.t.spacing[str(step)]}px"

    def h(self, size: str, inset: int = 2) -> str:
        """Content height for a control so its outer height matches the token."""
        return f"{self.t.control_height[size] - inset}px"

    def font(self, style: str) -> str:
        spec = self.t.typography[style]
        weight = min(max(spec.weight // 100 * 100, 400), 700)
        return f"font-size: {scaled(spec.size)}px; font-weight: {weight};"

    def mono(self) -> str:
        """A ``font-family`` declaration for code, limited to installed families."""
        from ...core.typography import _available

        return "font-family: " + ", ".join(f'"{name}"' for name in _available(self.t.mono_families)) + ";"

    def asset(self, name: str, role: str) -> str:
        return qss_asset(name, self.theme.colors[role])
