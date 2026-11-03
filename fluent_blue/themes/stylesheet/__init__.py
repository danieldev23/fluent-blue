"""Build the application stylesheet from a theme. One module per component group."""
from __future__ import annotations

from .context import Ctx


def build_stylesheet(theme) -> str:
    from . import base, buttons, data, display, feedback, inputs, navigation, selection, studio

    ctx = Ctx(theme)
    return "\n".join(m.build(ctx) for m in (base, buttons, inputs, selection, navigation, display, data, feedback, studio))
