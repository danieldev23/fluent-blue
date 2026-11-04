"""Foundations, Colors, Typography and Icons: the token reference, rendered live."""
from __future__ import annotations

from ... import (
    Button,
    Card,
    Column,
    DataTable,
    Grid,
    ScrollArea,
    SearchInput,
    SegmentedControl,
    Text,
    ThemeManager,
    Toast,
    icon,
    icon_names,
)
from ...compatibility.qt import (
    QApplication,
    QHBoxLayout,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPainter,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    QVBoxLayout,
    QWidget,
)
from ...components.base import ThemedMixin
from ...core.palette import contrast_ratio, readable_on
from ...core.tokens import TYPOGRAPHY


def page(title: str, description: str):
    """Return ``(page widget, content layout)`` with the standard page header."""
    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(24, 12, 24, 32)
    layout.setSpacing(16)
    layout.addWidget(Text(title, style="heading-1"))
    layout.addWidget(Text(description, style="body-large", color="text-secondary", wrap=True))
    shell = QWidget()
    outer = QVBoxLayout(shell)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.addWidget(ScrollArea(content))
    return shell, layout


class ColorCell(ThemedMixin, QWidget):
    """One token. Click to copy its value; the text color is chosen for contrast."""

    def __init__(self, role: str, label: str | None = None, height: int = 56) -> None:
        super().__init__()
        self.role, self.label = role, label or role
        self.setFixedHeight(height)
        self.setMinimumWidth(64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Copy {role}")
        self.setAccessibleName(role)
        self.bind_theme()

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802 - Qt override
        value = ThemeManager.color(self.role)
        QApplication.clipboard().setText(value)
        Toast.show(f"{self.role}: {value} copied", parent=self, variant="success", duration=1500)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        value = ThemeManager.color(self.role)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(ThemeManager.qcolor("border-subtle"))
        painter.setBrush(ThemeManager.qcolor(self.role))
        rect = QRectF(self.rect()).adjusted(.5, .5, -.5, -.5)
        painter.drawRoundedRect(rect, 6, 6)
        painter.setPen(ThemeManager.qcolor(readable_on(value[:7])))
        painter.setFont(ThemeManager.font("caption"))
        painter.drawText(rect.adjusted(8, 6, -4, -22), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), self.label)
        painter.drawText(rect.adjusted(8, 26, -4, -4), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), value)
        painter.end()


def _ramp(card, roles) -> None:
    row = QHBoxLayout()
    row.setSpacing(4)
    for role, label in roles:
        row.addWidget(ColorCell(role, label))
    card.content_layout().addLayout(row)


class _ContrastTable(ThemedMixin, DataTable):
    """WCAG ratios of key pairs, recalculated for the active theme."""

    def __init__(self, pairs) -> None:
        super().__init__([Column("pair", width=280), Column("ratio", width=90, align="right"), Column("level")], [], page_size=None,
                         selection="none", searchable=False, column_menu=False, exportable=False, row_height=30)
        self._pairs = pairs
        self.setFixedHeight(36 + 30 * len(pairs) + 6)
        self.bind_theme()
        self.refresh_theme()

    def refresh_theme(self) -> None:
        rows = []
        for fg, bg in self._pairs:
            ratio = contrast_ratio(ThemeManager.color(fg)[:7], ThemeManager.color(bg)[:7])
            rows.append({"pair": f"{fg} on {bg}", "ratio": f"{ratio:.2f}", "level": "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "Large text only"})
        self.set_rows(rows)


def colors_page() -> QWidget:
    shell, layout = page("Colors", "Primitive ramps and semantic roles of the active theme. Click any color to copy it.")
    primary = Card(title="Primary")
    _ramp(primary, [(f"primary-{k}", k) for k in ("50", "100", "200", "300", "400", "500", "600", "700", "800", "900")])
    layout.addWidget(primary)
    gray = Card(title="Neutral")
    _ramp(gray, [(f"gray-{k}", k) for k in ("0", "50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950", "1000")])
    layout.addWidget(gray)
    semantic = Card(title="Semantic")
    for name in ("success", "warning", "error", "info"):
        _ramp(semantic, [(name, name), (f"{name}-hover", "hover"), (f"{name}-pressed", "pressed"), (f"{name}-subtle", "subtle"), (f"{name}-border", "border"), (f"{name}-text", "text")])
    layout.addWidget(semantic)
    groups = (("Surface", ("background", "surface", "surface-secondary", "surface-tertiary", "surface-elevated", "surface-overlay")),
              ("Text", ("text-primary", "text-secondary", "text-tertiary", "text-disabled", "text-inverse")),
              ("Border", ("border", "border-subtle", "border-strong", "border-focus")))
    for title, roles in groups:
        card = Card(title=title)
        _ramp(card, [(r, r) for r in roles])
        layout.addWidget(card)

    ant_card = Card(title="Extended hues", subtitle="Twelve additional hue families with ten steps each, for charts, tags and data visualisation.")
    for name in ("blue", "green", "gold", "red", "volcano", "orange", "yellow", "lime", "cyan", "geekblue", "purple", "magenta"):
        _ramp(ant_card, [(f"{name}-{k}", str(k)) for k in range(1, 11)])
    layout.addWidget(ant_card)

    contrast = Card(title="Contrast", subtitle="WCAG 2.1 ratios of the key pairs in the active theme, recalculated on theme change.")
    pairs = (("text-primary", "surface"), ("text-secondary", "surface"), ("text-tertiary", "surface"), ("on-primary", "primary"), ("primary-text", "surface"), ("on-error", "error"))
    table = _ContrastTable(pairs)
    contrast.add(table)
    layout.addWidget(contrast)
    layout.addStretch(1)

    return shell


def typography_page() -> QWidget:
    shell, layout = page("Typography", "Segoe UI on Windows, with native fallbacks elsewhere. Sizes scale with configure(font_scale=…).")
    card = Card()
    for role, spec in TYPOGRAPHY.items():
        row = QHBoxLayout()
        name = Text(role, style="label", color="text-tertiary")
        name.setFixedWidth(110)
        row.addWidget(name)
        row.addWidget(Text("The quick brown fox jumps" if not spec.mono else "print('hello, world')", style=role), 1)
        row.addWidget(Text(f"{spec.size}/{spec.line_height}px · {spec.weight} · {spec.tracking:+g}px", style="caption", color="text-tertiary"))
        card.content_layout().addLayout(row)
    layout.addWidget(card)
    layout.addStretch(1)
    return shell


class IconsPage(ThemedMixin, QWidget):
    """Searchable grid of the icon set. Click an icon to copy its name."""

    def __init__(self) -> None:
        super().__init__()
        self._size = 20
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 12, 24, 16)
        layout.setSpacing(12)
        layout.addWidget(Text("Icons", style="heading-1"))
        layout.addWidget(Text(f"{len(icon_names())} original SVG icons on a 24 px grid with a 1.75 px stroke. They recolor with the theme.", style="body-large", color="text-secondary"))
        bar = QHBoxLayout()
        self.search = SearchInput(placeholder="Search icons…", debounce_ms=60)
        self.search.setMaximumWidth(320)
        self.search.search_changed.connect(self._fill)
        sizes = SegmentedControl([("16", 16), ("20", 20), ("24", 24), ("40", 40)], value=20)
        sizes.value_changed.connect(self._set_size)
        bar.addWidget(self.search)
        bar.addStretch(1)
        bar.addWidget(sizes)
        layout.addLayout(bar)
        self.grid = QListWidget()
        self.grid.setObjectName("iconGrid")
        self.grid.setViewMode(QListView.ViewMode.IconMode)
        self.grid.setResizeMode(QListView.ResizeMode.Adjust)
        self.grid.setMovement(QListView.Movement.Static)
        self.grid.setUniformItemSizes(True)
        self.grid.setGridSize(QSize(112, 84))
        self.grid.itemClicked.connect(self._copy)
        self.grid.itemActivated.connect(self._copy)
        layout.addWidget(self.grid, 1)
        self.bind_theme()
        self._fill("")

    def refresh_theme(self) -> None:
        self._fill(self.search.text())

    def _set_size(self, size: int) -> None:
        self._size = size
        self._fill(self.search.text())

    def _fill(self, query: str) -> None:
        self.grid.clear()
        self.grid.setIconSize(QSize(self._size, self._size))
        for name in icon_names():
            if query.lower() in name:
                self.grid.addItem(QListWidgetItem(icon(name, self._size, "text-primary"), name))

    def _copy(self, item) -> None:
        QApplication.clipboard().setText(item.text())
        Toast.show(f"{item.text()} copied", parent=self, variant="success", duration=1400)


class _ScaleBar(QWidget):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.setFixedSize(max(1, width), 14)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.fillRect(self.rect(), ThemeManager.qcolor("primary"))
        painter.end()


class _RadiusTile(QWidget):
    def __init__(self, radius: int) -> None:
        super().__init__()
        self.radius = radius
        self.setFixedSize(72, 56)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(ThemeManager.qcolor("primary-subtle"))
        painter.setPen(ThemeManager.qcolor("primary"))
        r = min(self.radius, 27.5)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), r, r)
        painter.end()


def foundations_page() -> QWidget:
    shell, layout = page("Foundations", "Spacing, radius, elevation and motion tokens. Components consume these and nothing else.")
    tokens = ThemeManager.tokens
    grid = Grid(columns=2, gap=4)
    spacing = Card(title="Spacing", subtitle="A 4 px scale. ThemeManager.spacing(step).")
    for step, value in tokens.spacing.items():
        row = QHBoxLayout()
        name = Text(f"spacing-{step}", style="label", color="text-secondary")
        name.setFixedWidth(84)
        row.addWidget(name)
        row.addWidget(_ScaleBar(value))
        row.addWidget(Text(f"{value}px", style="label", color="text-secondary"))
        row.addStretch(1)
        spacing.add_layout = spacing.content_layout().addLayout(row)
    grid.add(spacing)
    right = QWidget()
    column = QVBoxLayout(right)
    column.setContentsMargins(0, 0, 0, 0)
    column.setSpacing(ThemeManager.spacing(4))
    radius = Card(title="Radius")
    row = QHBoxLayout()
    for name, value in tokens.radius.items():
        cell = QVBoxLayout()
        cell.addWidget(_RadiusTile(value))
        cell.addWidget(Text(name, style="label", color="text-secondary"), 0, Qt.AlignmentFlag.AlignHCenter)
        row.addLayout(cell)
    row.addStretch(1)
    radius.content_layout().addLayout(row)
    column.addWidget(radius)
    elevation = Card(title="Elevation")
    row = QHBoxLayout()
    row.setSpacing(20)
    for level in tokens.elevation:
        tile = Card(elevation=level)
        tile.setFixedHeight(64)
        tile.content_layout().addWidget(Text(f"Level {level}", style="label"))
        row.addWidget(tile)
    elevation.content_layout().addLayout(row)
    column.addWidget(elevation)
    motion = Card(title="Motion", subtitle="Run each duration and easing token.")
    track = QWidget()
    track.setFixedHeight(36)
    dot = Card(track, tone="brand")
    dot.setGeometry(0, 2, 32, 32)
    row = QHBoxLayout()
    animation = QPropertyAnimation(dot, b"geometry", motion)

    def run(name: str, easing: str) -> None:
        animation.stop()
        animation.setDuration(max(ThemeManager.duration(name), 1))
        animation.setEasingCurve(ThemeManager.easing(easing))
        left = dot.x() < 8
        target = track.width() - 32 if left else 0
        animation.setStartValue(dot.geometry())
        animation.setEndValue(QRect(target, 2, 32, 32))
        animation.start()

    for name, easing in (("fast", "standard"), ("normal", "standard"), ("slow", "standard"), ("slow", "emphasized")):
        value = ThemeManager.duration(name)
        button = Button(f"{name} {value}ms · {easing}", size="small")
        button.clicked.connect(lambda _=False, n=name, e=easing: run(n, e))
        row.addWidget(button)
    row.addStretch(1)
    motion.content_layout().addLayout(row)
    motion.add(track)
    column.addWidget(motion)
    column.addStretch(1)
    grid.add(right)
    layout.addWidget(grid)
    layout.addStretch(1)
    return shell
