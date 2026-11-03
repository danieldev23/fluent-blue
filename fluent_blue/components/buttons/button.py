"""Button family. Styling comes from the ``variant`` and ``fbSize`` stylesheet selectors."""
from __future__ import annotations

from ...compatibility.qt import QIcon, QPushButton, QSize, QSizePolicy, Qt, QTimer
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ..base import ThemedMixin, apply_common, check_choice, set_style_prop, spinner_pixmap

VARIANTS = ("primary", "secondary", "outline", "ghost", "text", "danger")
SIZES = ("small", "medium", "large")
_ICON_ROLE = {
    "primary": "on-primary", "danger": "on-error", "secondary": "text-primary",
    "outline": "primary-text", "ghost": "text-secondary", "text": "primary-text",
}
_ICON_PX = {"small": 14, "medium": 16, "large": 18}


class Button(ThemedMixin, QPushButton):
    """A push button with variants, sizes, icons and a loading state.

    Args:
        text: Button label.
        parent: Parent widget.
        variant: ``primary``, ``secondary``, ``outline``, ``ghost``, ``text`` or ``danger``.
        size: ``small``, ``medium`` or ``large``.
        icon: Icon name or ``QIcon``.
        icon_position: ``left`` or ``right``.
        loading: Show a spinner and ignore clicks.
        disabled: Start disabled.
        full_width: Expand to fill the available width.
        tooltip: Tooltip text.
    """

    DEFAULT_VARIANT = "secondary"

    def __init__(self, text: str = "", parent=None, *, variant: str | None = None, size: str = "medium",
                 icon: str | QIcon | None = None, icon_position: str = "left", loading: bool = False,
                 disabled: bool = False, full_width: bool = False, tooltip: str | None = None) -> None:
        super().__init__(text, parent)
        self._icon_source = icon
        self._loading = False
        self._angle = 0.0
        self._spinner = None
        self.bind_theme()
        # Tab-only focus: a mouse click should not leave a focus ring behind.
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_variant(variant or self.DEFAULT_VARIANT)
        self.set_size(size)
        self.set_icon_position(icon_position)
        self.set_full_width(full_width)
        apply_common(self, disabled=disabled, tooltip=tooltip)
        self.set_loading(loading)

    # ---- public API ----------------------------------------------------------
    def variant(self) -> str:
        return self.property("variant")

    def set_variant(self, variant: str) -> None:
        check_choice("variant", variant, VARIANTS)
        set_style_prop(self, "variant", variant)
        self._update_icon()

    def size_name(self) -> str:
        return self.property("fbSize")

    def set_size(self, size: str) -> None:
        check_choice("size", size, SIZES)
        set_style_prop(self, "fbSize", size)
        self.setIconSize(QSize(_ICON_PX[size], _ICON_PX[size]))
        self._update_icon()

    def set_icon(self, icon: str | QIcon | None) -> None:
        """Set the icon by name or ``QIcon``; ``None`` removes it."""
        self._icon_source = icon
        self._update_icon()

    def set_icon_position(self, position: str) -> None:
        check_choice("icon_position", position, ("left", "right"))
        direction = Qt.LayoutDirection.RightToLeft if position == "right" else Qt.LayoutDirection.LeftToRight
        self.setLayoutDirection(direction)

    def set_full_width(self, full: bool) -> None:
        policy = QSizePolicy.Policy.Expanding if full else QSizePolicy.Policy.Fixed
        self.setSizePolicy(policy, QSizePolicy.Policy.Fixed)

    def is_loading(self) -> bool:
        return self._loading

    def set_loading(self, loading: bool) -> None:
        """Show or hide the spinner. While loading, the button ignores clicks and keys."""
        if loading == self._loading:
            return
        self._loading = loading
        self.setAccessibleDescription("Loading" if loading else "")
        self.setCursor(Qt.CursorShape.BusyCursor if loading else Qt.CursorShape.PointingHandCursor)
        if loading:
            if self._spinner is None:
                self._spinner = QTimer(self)
                self._spinner.setInterval(40)
                self._spinner.timeout.connect(self._tick)
            self._spinner.start()
            self._tick()
        else:
            if self._spinner:
                self._spinner.stop()
            self._update_icon()

    def setMenu(self, menu) -> None:  # noqa: N802 - Qt override
        super().setMenu(menu)
        set_style_prop(self, "hasMenu", "true" if menu else "false")

    # ---- internals -----------------------------------------------------------
    def refresh_theme(self) -> None:
        self._update_icon()

    def _icon_role(self) -> str:
        return _ICON_ROLE.get(self.property("variant"), "text-primary")

    def _update_icon(self) -> None:
        if self._loading or self.property("fbSize") is None:
            return
        source = self._icon_source
        if source is None:
            self.setIcon(QIcon())
        elif isinstance(source, QIcon):
            self.setIcon(source)
        else:
            self.setIcon(make_icon(source, self.iconSize().width(), self._icon_role()))

    def _tick(self) -> None:
        self._angle = (self._angle + 24) % 360
        px = self.iconSize().width()
        self.setIcon(QIcon(spinner_pixmap(px, ThemeManager.color(self._icon_role()), self._angle)))

    def hitButton(self, pos) -> bool:  # noqa: N802 - Qt override
        return not self._loading and super().hitButton(pos)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._loading and event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            return
        super().keyPressEvent(event)


class PrimaryButton(Button):
    """The single most important action in a view."""

    DEFAULT_VARIANT = "primary"


class SecondaryButton(Button):
    """A standard action. This is the default look of ``Button``."""

    DEFAULT_VARIANT = "secondary"


class OutlineButton(Button):
    """A brand-tinted action with less weight than ``PrimaryButton``."""

    DEFAULT_VARIANT = "outline"


class GhostButton(Button):
    """A low-emphasis action for toolbars and dense layouts."""

    DEFAULT_VARIANT = "ghost"


class TextButton(Button):
    """A link-like action, typically inline with content."""

    DEFAULT_VARIANT = "text"


class DangerButton(Button):
    """A destructive action, such as deleting data."""

    DEFAULT_VARIANT = "danger"


class LoadingButton(Button):
    """A primary button with ``start()`` and ``stop()`` shortcuts for async work.

    Args:
        loading_text: Label to show while loading; the original label returns on ``stop()``.
    """

    DEFAULT_VARIANT = "primary"

    def __init__(self, text: str = "", parent=None, *, loading_text: str | None = None, **kwargs) -> None:
        self._loading_text = loading_text
        self._idle_text = text
        super().__init__(text, parent, **kwargs)

    def start(self) -> None:
        """Enter the loading state."""
        self._idle_text = self.text()
        if self._loading_text:
            self.setText(self._loading_text)
        self.set_loading(True)

    def stop(self) -> None:
        """Leave the loading state and restore the label."""
        self.set_loading(False)
        self.setText(self._idle_text)


class IconButton(Button):
    """A square icon-only button.

    Args:
        icon: Icon name or ``QIcon``.
        tooltip: Also used as the accessible name, which an icon-only control needs.
    """

    DEFAULT_VARIANT = "ghost"
    _PX = {"small": 28, "medium": 34, "large": 40}

    def __init__(self, icon: str | QIcon, parent=None, *, variant: str | None = None, size: str = "medium",
                 tooltip: str | None = None, disabled: bool = False, loading: bool = False,
                 checkable: bool = False) -> None:
        super().__init__("", parent, variant=variant, size=size, icon=icon, tooltip=tooltip,
                         disabled=disabled, loading=loading)
        self.setCheckable(checkable)
        self.setAccessibleName(tooltip or (icon if isinstance(icon, str) else ""))

    def set_size(self, size: str) -> None:
        super().set_size(size)
        side = ThemeManager.tokens.control_height[size]
        self.setFixedSize(side, side)
