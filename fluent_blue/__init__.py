"""Fluent Blue: a design system for PyQt6 and PySide6 desktop applications.

>>> from fluent_blue import Button, ThemeManager  # doctest: +SKIP
"""
from .compatibility import BINDING, BINDING_VERSION, QT_VERSION
from .components import advanced, buttons, data, display, feedback, inputs, layout, navigation, selection
from .components.advanced import *  # noqa: F403
from .components.buttons import *  # noqa: F403
from .components.data import *  # noqa: F403
from .components.display import *  # noqa: F403
from .components.feedback import *  # noqa: F403
from .components.inputs import *  # noqa: F403
from .components.layout import *  # noqa: F403
from .components.navigation import *  # noqa: F403
from .components.selection import *  # noqa: F403
from .core import Configuration, DesignTokens, Theme, ThemeManager, config, configure
from .icons import has_icon, icon, icon_names, icon_pixmap, register_icon, register_icon_file

__version__ = "0.1.0"

__all__ = [
    "BINDING", "BINDING_VERSION", "QT_VERSION", "Configuration", "DesignTokens", "Theme", "ThemeManager", "__version__",
    "config", "configure", "has_icon", "icon", "icon_names", "icon_pixmap", "register_icon", "register_icon_file",
]
for _module in (advanced, buttons, data, display, feedback, inputs, layout, navigation, selection):
    __all__ += _module.__all__
del _module
