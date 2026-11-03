"""SVG icon rendering, registration and theme-aware lookup."""
from __future__ import annotations

import atexit
import hashlib
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from ..compatibility.qt import (
    QApplication, QByteArray, QIcon, QImage, QPainter, QPixmap, QRectF, QSize, QSvgRenderer, Qt,
)
from ..core.theme_manager import ThemeManager
from .library import ICONS

STROKE_WIDTH = 1.75
FALLBACK_ICON = "__fallback__"
_FALLBACK = '<rect x="4.5" y="4.5" width="15" height="15" rx="2" stroke-dasharray="3 3"/>'
_custom: dict[str, str] = {}
_assets_dir: Path | None = None


def register_icon(name: str, svg: str) -> None:
    """Register or replace an icon.

    Args:
        name: Icon name used everywhere an ``icon`` argument is accepted.
        svg: Either inner markup for a 24x24 canvas, or a complete ``<svg>`` document.
            Use ``currentColor`` wherever the theme color should apply.
    """
    _custom[name] = svg
    _render.cache_clear()
    _cached_pixmap.cache_clear()
    _cached_icon.cache_clear()


def register_icon_file(name: str, path: str | Path) -> None:
    """Register an icon from an SVG file."""
    register_icon(name, Path(path).read_text(encoding="utf-8"))


def icon_names() -> list[str]:
    """Sorted names of all available icons."""
    return sorted({*ICONS, *_custom})


def has_icon(name: str) -> bool:
    return name in _custom or name in ICONS


def icon_svg(name: str, color: str = "#000000") -> str:
    """Full SVG document for ``name``; unknown names return a visible fallback glyph."""
    markup = _custom.get(name) or ICONS.get(name) or _FALLBACK
    if "<svg" in markup:
        return markup.replace("currentColor", color)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="{STROKE_WIDTH}" stroke-linecap="round" stroke-linejoin="round">'
        f"{markup.replace('currentColor', color)}</svg>"
    )


@lru_cache(maxsize=2048)
def _render(name: str, size: int, color: str, ratio: float) -> QImage:
    pixels = max(1, round(size * ratio))
    image = QImage(pixels, pixels, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(icon_svg(name, color).encode()))
    painter = QPainter(image)
    renderer.render(painter, QRectF(0, 0, pixels, pixels))
    painter.end()
    return image


def _device_ratio() -> float:
    app = QApplication.instance()
    screen = app.primaryScreen() if app else None
    return screen.devicePixelRatio() if screen else 1.0


def _resolve(color: str) -> str:
    return color if color.startswith("#") else ThemeManager.color(color)


@lru_cache(maxsize=2048)
def _cached_pixmap(name: str, size: int, resolved: str, ratio: float) -> QPixmap:
    pixmap = QPixmap.fromImage(_render(name, size, resolved, ratio))
    pixmap.setDevicePixelRatio(ratio)
    return pixmap


def icon_pixmap(name: str, size: int = 16, color: str = "text-secondary", ratio: float | None = None) -> QPixmap:
    """Render an icon to a crisp pixmap. ``color`` is a color role or hex value. Results are cached."""
    return _cached_pixmap(name, size, _resolve(color)[:7], ratio or _device_ratio())


@lru_cache(maxsize=2048)
def _cached_icon(name: str, size: int, color: str, disabled: str, ratio: float) -> QIcon:
    result = QIcon()
    normal = _cached_pixmap(name, size, color, ratio)
    result.addPixmap(normal, QIcon.Mode.Normal)
    result.addPixmap(_cached_pixmap(name, size, disabled, ratio), QIcon.Mode.Disabled)
    result.addPixmap(normal, QIcon.Mode.Active)
    result.addPixmap(normal, QIcon.Mode.Selected)
    return result


def icon(name: str, size: int = 16, color: str = "text-secondary", disabled_color: str = "text-disabled") -> QIcon:
    """Build a ``QIcon`` with normal and disabled modes from the current theme. Results are cached."""
    return _cached_icon(name, size, _resolve(color)[:7], _resolve(disabled_color)[:7], _device_ratio())


def icon_size(size: int) -> QSize:
    return QSize(size, size)


def qss_asset(name: str, color: str) -> str:
    """Write a colored SVG to a per-process temp directory and return a path usable in ``url()``."""
    global _assets_dir
    if _assets_dir is None:
        _assets_dir = Path(tempfile.mkdtemp(prefix="fluent_blue_"))
        atexit.register(shutil.rmtree, _assets_dir, ignore_errors=True)
    digest = hashlib.sha1(f"{name}{color}".encode()).hexdigest()[:12]
    path = _assets_dir / f"{name}-{digest}.svg"
    if not path.exists():
        path.write_text(icon_svg(name, color[:7]), encoding="utf-8")
    return path.as_posix()
