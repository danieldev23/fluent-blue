"""Runtime theme engine.

Propagation strategy, chosen to keep theme switches cheap:

* One stylesheet is generated per theme and set on the ``QApplication``. Components
  carry no stylesheets of their own, so a switch restyles the whole tree in one pass.
* Custom-painted components read colors from :data:`ThemeManager` at paint time.
* Anything cached (icons, shadows) refreshes through the ``theme_changed`` signal.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..compatibility.qt import QApplication, QColor, QEasingCurve, QFont, QObject, QPalette, Qt, Signal
from .configuration import config
from .palette import apply_overrides, dark_colors, high_contrast_colors, light_colors, parse_hex
from .tokens import DesignTokens, Shadow
from .typography import make_font


@dataclass
class Theme:
    """A complete, resolved theme."""

    name: str
    is_dark: bool
    colors: dict[str, str]
    tokens: DesignTokens = field(default_factory=DesignTokens)
    label: str = ""


class _ThemeManager(QObject):
    """Singleton behind the public :data:`ThemeManager` name."""

    theme_about_to_change = Signal(str)
    """Emitted before a switch, so that hosts can drop hidden content and make it cheaper."""

    theme_changed = Signal(str)
    """Emitted with the theme name after the new theme is applied."""

    def __init__(self) -> None:
        super().__init__()
        self._themes: dict[str, Theme] = {}
        self._current: Theme | None = None
        self._applied_to: object | None = None
        self._follow_system = False
        self._system_hooked = False
        self._style_cache: dict[tuple[str, float], str] = {}
        self._font_cache: dict[tuple, object] = {}
        self._fusion_applied = False
        self._themes["light"] = Theme("light", False, light_colors(), label="Fluent Blue Light")
        self._themes["dark"] = Theme("dark", True, dark_colors(), label="Fluent Blue Dark")
        self._themes["high-contrast"] = Theme("high-contrast", True, high_contrast_colors(), label="High Contrast")
        self._current = self._themes["light"]

    # ---- registry ----------------------------------------------------------------
    def themes(self) -> list[str]:
        """Names of all registered themes."""
        return list(self._themes)

    def theme(self, name: str | None = None) -> Theme:
        """Return a theme by name, or the current theme."""
        if name is None:
            return self._current
        try:
            return self._themes[name]
        except KeyError:
            raise KeyError(f"Unknown theme {name!r}. Registered: {', '.join(self._themes)}") from None

    def register_theme(self, name: str, definition: dict | None = None) -> Theme:
        """Register or replace a custom theme.

        Args:
            name: Theme name passed later to :meth:`set_theme`.
            definition: Optional keys are ``base`` (a registered theme to extend,
                default ``"light"``), ``colors`` (role overrides; ``text_primary`` and
                ``text-primary`` are equivalent), ``tokens`` (token group overrides)
                and ``label``. Overriding ``primary`` regenerates the primary ramp.
        """
        definition = dict(definition or {})
        base = self.theme(definition.pop("base", "light"))
        colors = apply_overrides(base.colors, definition.pop("colors", None), base.is_dark)
        tokens = base.tokens.merged(definition.pop("tokens", None))
        label = definition.pop("label", name.replace("-", " ").title())
        if definition:
            raise KeyError(f"Unknown theme keys: {', '.join(definition)}")
        theme = Theme(name, base.is_dark, colors, tokens, label)
        self._themes[name] = theme
        self._style_cache = {k: v for k, v in self._style_cache.items() if k[0] != name}
        self._font_cache = {k: v for k, v in self._font_cache.items() if k[0] != name}
        if self._current and self._current.name == name:
            self._current = theme
            self._apply(force=True)
        return theme

    def unregister_theme(self, name: str) -> None:
        """Remove a custom theme. Built-in themes and the active theme are protected."""
        if name in ("light", "dark", "high-contrast"):
            raise ValueError(f"Cannot unregister built-in theme {name!r}.")
        if self._current.name == name:
            raise ValueError("Cannot unregister the active theme.")
        self.theme(name)
        del self._themes[name]

    # ---- switching ----------------------------------------------------------------
    def set_theme(self, name: str) -> None:
        """Activate a theme by name; ``"system"`` follows the OS color scheme."""
        if name == "system":
            self._follow_system = True
            self._hook_system()
            name = "dark" if self._system_is_dark() else "light"
        else:
            self._follow_system = False
        target = self.theme(name)
        changed = target is not self._current
        if not changed:
            self._apply(force=False)
            return
        self.theme_about_to_change.emit(name)
        # One repaint for the whole switch, instead of one per restyled widget.
        windows = [w for w in QApplication.topLevelWidgets() if w.isVisible()] if QApplication.instance() else []
        for window in windows:
            window.setUpdatesEnabled(False)
        try:
            self._current = target
            self._apply(force=True)
            self.theme_changed.emit(name)
        finally:
            for window in windows:
                window.setUpdatesEnabled(True)

    def toggle(self) -> str:
        """Switch between light and dark; returns the new theme name."""
        name = "light" if self._current.is_dark else "dark"
        self.set_theme(name)
        return name

    def current(self) -> str:
        """Name of the active theme."""
        return self._current.name

    def is_dark(self) -> bool:
        return self._current.is_dark

    def refresh(self) -> None:
        """Re-apply the active theme, for example after changing :data:`config`."""
        self._style_cache.clear()
        self._font_cache.clear()
        self._apply(force=True)
        self.theme_changed.emit(self._current.name)

    def ensure_applied(self) -> None:
        """Apply the theme to the application if that has not happened yet.

        Components call this on construction, so a theme is present even if the
        developer never calls :meth:`set_theme`.
        """
        app = QApplication.instance()
        if app is not None and app is not self._applied_to:
            self._apply(force=True)

    # ---- token access ---------------------------------------------------------------
    def color(self, role: str) -> str:
        """Hex value of a color role such as ``"text-primary"``."""
        return self._current.colors[role.replace("_", "-")]

    def qcolor(self, role: str, alpha: float | None = None) -> QColor:
        """``QColor`` for a color role or literal hex value, with optional alpha override."""
        value = role if role.startswith("#") else self.color(role)
        r, g, b, a = parse_hex(value)
        return QColor(r, g, b, a if alpha is None else round(255 * alpha))

    @property
    def tokens(self) -> DesignTokens:
        return self._current.tokens

    def spacing(self, step: int | str) -> int:
        return self.tokens.spacing[str(step)]

    def radius(self, name: str) -> int:
        return self.tokens.radius[name]

    def shadow(self, level: int) -> Shadow:
        return self.tokens.elevation[level]

    def font(self, style: str = "body-medium"):
        """``QFont`` for a typography role. Cached, because painting calls this constantly."""
        tokens = self.tokens
        key = (self._current.name, style, config.font_scale)
        cached = self._font_cache.get(key)
        if cached is None:
            cached = make_font(tokens.typography[style], families=tokens.font_families, mono_families=tokens.mono_families)
            self._font_cache[key] = cached
        return QFont(cached)

    def duration(self, name: str = "normal") -> int:
        """Animation duration in ms; 0 when animations are disabled."""
        return int(self.tokens.motion[f"duration-{name}"]) if config.animations else 0

    def easing(self, name: str = "standard") -> QEasingCurve:
        return QEasingCurve(getattr(QEasingCurve.Type, str(self.tokens.motion[f"easing-{name}"])))

    def stylesheet(self) -> str:
        """The generated application stylesheet for the active theme."""
        from ..themes.stylesheet import build_stylesheet

        key = (self._current.name, config.font_scale)
        if key not in self._style_cache:
            self._style_cache[key] = build_stylesheet(self._current)
        return self._style_cache[key]

    # ---- internals --------------------------------------------------------------------
    def _apply(self, force: bool) -> None:
        app = QApplication.instance()
        if app is None:
            return  # Applied by the first component, or the next set_theme call.
        if not force and app is self._applied_to:
            return
        if config.use_fusion_style and not self._fusion_applied:
            # Once only. Under a stylesheet, style() is a proxy that never reports "fusion",
            # so checking its name would restyle every widget on each switch.
            app.setStyle("Fusion")
            self._fusion_applied = True
        app.setPalette(self._build_palette())
        if config.apply_app_font:
            app.setFont(self.font("body-medium"))
        app.setStyleSheet(self.stylesheet())
        self._applied_to = app

    def _build_palette(self) -> QPalette:
        palette = QPalette()
        role = QPalette.ColorRole
        for target, source in (
            (role.Window, "background"), (role.WindowText, "text-primary"), (role.Base, "surface"),
            (role.AlternateBase, "surface-secondary"), (role.Text, "text-primary"),
            (role.Button, "control"), (role.ButtonText, "text-primary"),
            (role.BrightText, "text-inverse"), (role.ToolTipBase, "surface-elevated"),
            (role.ToolTipText, "text-primary"), (role.Highlight, "primary"),
            (role.HighlightedText, "on-primary"), (role.Link, "primary-text"),
            (role.LinkVisited, "primary-text"), (role.PlaceholderText, "text-tertiary"),
        ):
            palette.setColor(target, self.qcolor(source))
        disabled = QPalette.ColorGroup.Disabled
        for target in (role.WindowText, role.Text, role.ButtonText):
            palette.setColor(disabled, target, self.qcolor("text-disabled"))
        return palette

    def _system_is_dark(self) -> bool:
        app = QApplication.instance()
        return bool(app and app.styleHints().colorScheme() == Qt.ColorScheme.Dark)

    def _hook_system(self) -> None:
        app = QApplication.instance()
        if app and not self._system_hooked:
            app.styleHints().colorSchemeChanged.connect(self._on_system_scheme)
            self._system_hooked = True

    def _on_system_scheme(self, _scheme=None) -> None:
        if self._follow_system:
            self.set_theme("system")


ThemeManager = _ThemeManager()
"""The global theme engine. Use it directly: ``ThemeManager.set_theme("dark")``."""


def configure(**settings) -> None:
    """Update :class:`~fluent_blue.core.configuration.Configuration` and re-apply the theme."""
    for key, value in settings.items():
        if not hasattr(config, key):
            raise KeyError(f"Unknown setting {key!r}")
        setattr(config, key, value)
    ThemeManager.refresh()
