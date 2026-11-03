"""SVG icon system. See :func:`icon` and :func:`register_icon`."""
from .engine import has_icon, icon, icon_names, icon_pixmap, icon_size, icon_svg, register_icon, register_icon_file
from .library import ICONS

__all__ = [
    "ICONS", "has_icon", "icon", "icon_names", "icon_pixmap", "icon_size", "icon_svg",
    "register_icon", "register_icon_file",
]
