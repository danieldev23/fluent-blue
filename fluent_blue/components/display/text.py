"""Typography, badges, tags, dividers."""
from __future__ import annotations

from ...compatibility.qt import QFont, QFrame, QHBoxLayout, QLabel, QPainter, QSize, QSizePolicy, Qt, QToolButton, QWidget, Signal
from ...core.theme_manager import ThemeManager
from ...core.tokens import TYPOGRAPHY
from ...icons import icon as make_icon
from ..base import ThemedMixin, check_choice, set_style_prop

BADGE_VARIANTS = ("neutral", "primary", "success", "warning", "error", "info")


class Text(QLabel):
    """A label bound to a typography role and a text color role.

    Args:
        text: Content.
        style: Typography role such as ``heading-2`` or ``body-medium``.
        color: Text color role such as ``text-secondary``.
        wrap: Enable word wrap.
        selectable: Allow mouse selection.
    """

    def __init__(self, text: str = "", parent=None, *, style: str = "body-medium", color: str = "text-primary",
                 wrap: bool = False, selectable: bool = False) -> None:
        super().__init__(text, parent)
        ThemeManager.ensure_applied()
        self.set_style(style)
        self.set_color(color)
        self.setWordWrap(wrap)
        if selectable:
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def set_style(self, style: str) -> None:
        check_choice("style", style, TYPOGRAPHY)
        set_style_prop(self, "textStyle", style)
        tracking = ThemeManager.tokens.typography[style].tracking
        font = self.font()
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, tracking)
        if ThemeManager.tokens.typography[style].mono:
            font.setFamilies(ThemeManager.font("monospace").families())
        self.setFont(font)

    def set_color(self, color: str) -> None:
        set_style_prop(self, "textColor", color)


class Badge(QLabel):
    """A small status label or dot.

    Args:
        text: Content; empty with ``dot=True``.
        variant: ``neutral``, ``primary``, ``success``, ``warning``, ``error`` or ``info``.
        dot: Render as a small dot.
    """

    def __init__(self, text: str = "", parent=None, *, variant: str = "neutral", dot: bool = False) -> None:
        super().__init__("" if dot else text, parent)
        ThemeManager.ensure_applied()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setProperty("dot", "true" if dot else "false")
        if dot and text:
            self.setAccessibleName(text)
        self.set_variant(variant)

    def variant(self) -> str:
        return self.property("variant")

    def set_variant(self, variant: str) -> None:
        check_choice("variant", variant, BADGE_VARIANTS)
        set_style_prop(self, "variant", variant)


class BadgeOverlay(QWidget):
    """Wraps any child widget and pins a Badge to its top-right corner.

    Args:
        target: The target widget to wrap (e.g., an IconButton, Avatar, or Button).
        text: Count or label for the badge.
        variant: Status role for the badge (default ``error`` for notification dots/numbers).
        dot: If True, renders as an unlabelled indicator dot.
    """

    def __init__(
        self,
        target: QWidget,
        text: str = "",
        parent=None,
        *,
        variant: str = "error",
        dot: bool = False,
    ) -> None:
        super().__init__(parent)
        self._target = target
        self._target.setParent(self)

        self._badge = Badge(text, self, variant=variant, dot=dot)
        self._badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._target)

        self._position_badge()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._position_badge()

    def _position_badge(self) -> None:
        bw, bh = self._badge.sizeHint().width(), self._badge.sizeHint().height()
        # Pin to upper right edge
        x = max(0, self.width() - bw + 2)
        y = max(0, -2)
        self._badge.setGeometry(x, y, max(bw, 14), max(bh, 14))
        self._badge.raise_()

    def set_text(self, text: str) -> None:
        self._badge.setText(text)
        self._position_badge()

    def set_variant(self, variant: str) -> None:
        self._badge.set_variant(variant)

    def set_visible_badge(self, visible: bool) -> None:
        self._badge.setVisible(visible)



class Tag(ThemedMixin, QFrame):
    """A compact label for categories, optionally closable.

    Args:
        text: Content.
        variant: Same options as :class:`Badge`.
        closable: Show a close button.

    Signals:
        closed(str): The close button was used; carries the text. The tag hides itself.
    """

    closed = Signal(str)

    def __init__(self, text: str = "", parent=None, *, variant: str = "neutral", closable: bool = False) -> None:
        super().__init__(parent)
        check_choice("variant", variant, BADGE_VARIANTS)
        self.setProperty("variant", variant)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(24)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 4 if closable else 8, 0)
        layout.setSpacing(4)
        self.label = QLabel(text)
        layout.addWidget(self.label)
        self.close_button = None
        self.bind_theme()
        if closable:
            self.close_button = QToolButton()
            self.close_button.setFixedSize(16, 16)
            self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.close_button.setAccessibleName(f"Remove {text}")
            self.close_button.clicked.connect(self._close)
            self.refresh_theme()
            layout.addWidget(self.close_button)

    def text(self) -> str:
        return self.label.text()

    def refresh_theme(self) -> None:
        if self.close_button:
            self.close_button.setIcon(make_icon("close", 12, "text-secondary"))

    def _close(self) -> None:
        self.hide()
        self.closed.emit(self.text())


class Divider(QWidget):
    """A separator line, optionally with centered text.

    Args:
        text: Optional caption on a horizontal divider.
        orientation: ``horizontal`` or ``vertical``.
    """

    def __init__(self, text: str = "", parent=None, *, orientation: str = "horizontal") -> None:
        super().__init__(parent)
        check_choice("orientation", orientation, ("horizontal", "vertical"))
        ThemeManager.ensure_applied()
        self._text = text
        self._vertical = orientation == "vertical"
        fixed, expanding = QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        self.setSizePolicy(fixed, expanding) if self._vertical else self.setSizePolicy(expanding, fixed)

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(1, 16) if self._vertical else QSize(16, 18 if self._text else 1)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setPen(ThemeManager.qcolor("border"))
        w, h = self.width(), self.height()
        if self._vertical:
            painter.drawLine(w // 2, 0, w // 2, h)
        elif self._text:
            painter.setFont(ThemeManager.font("caption"))
            advance = painter.fontMetrics().horizontalAdvance(self._text)
            left = (w - advance) // 2 - 10
            painter.drawLine(0, h // 2, max(0, left), h // 2)
            painter.drawLine(min(w, left + advance + 20), h // 2, w, h // 2)
            painter.setPen(ThemeManager.qcolor("text-tertiary"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)
        else:
            painter.drawLine(0, h // 2, w, h // 2)
        painter.end()
