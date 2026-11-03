"""The Overview bento board. Every tile holds real, interactive components."""
from __future__ import annotations

from ... import (
    Alert, Avatar, Badge, Breadcrumb, Button, Card, Checkbox, CircularProgress, ComboBox, ConfirmDialog, DropdownMenu, GhostButton,
    IconButton, Input, ListItem, Popover, PrimaryButton, ProgressBar, RadioButton, RadioGroup, ScrollArea, SearchInput,
    SegmentedControl, Select, Sidebar, Slider, Switch, Tabs, Text, TextButton, ThemeManager, Toast, ToastCard,
)
from ...compatibility.qt import (
    QApplication, QButtonGroup, QFrame, QHBoxLayout, QLabel, QLinearGradient, QListWidget, QListWidgetItem, QPainter, QPen, QRectF,
    QSize, Qt, QTimer, QVBoxLayout, QWidget, Signal,
)
from ...components.base import ThemedMixin
from ...core.animations import apply_elevation
from ...icons import icon as make_icon
from ...icons import icon_pixmap
from ..art import HeroCard, LandscapeArt, draw_waves

SECTION_GAP = 12


def copy_text(text: str, anchor, note: str = "Copied to clipboard") -> None:
    QApplication.clipboard().setText(text)
    Toast.show(note, parent=anchor, variant="success", duration=1600)


class BentoCard(QFrame):
    """A titled tile with a Copy button that copies the code which builds its content."""

    def __init__(self, title: str, code: str = "", parent=None) -> None:
        super().__init__(parent)
        self.code = code
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 12)
        outer.setSpacing(10)
        header = QHBoxLayout()
        label = QLabel(title)
        label.setObjectName("bentoTitle")
        header.addWidget(label)
        header.addStretch(1)
        if code:
            copy = Button("Copy", size="small", tooltip=f"Copy the {title} code")
            copy.setProperty("pill", "true")
            copy.clicked.connect(lambda: copy_text(self.code, self, f"{title} code copied"))
            header.addWidget(copy)
        outer.addLayout(header)
        self.body = QVBoxLayout()
        self.body.setSpacing(8)
        outer.addLayout(self.body, 1)


class SwatchTile(ThemedMixin, QWidget):
    """A color role: click to copy its current value."""

    def __init__(self, label: str, role: str) -> None:
        super().__init__()
        self.label, self.role = label, role
        self.setFixedHeight(74)
        self.setMinimumWidth(56)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAccessibleName(f"{label} color")
        self.setToolTip("Click to copy")
        self.bind_theme()

    def _copy(self) -> None:
        copy_text(ThemeManager.color(self.role), self, f"{self.label} {ThemeManager.color(self.role)} copied")

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802 - Qt override
        self._copy()

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Space):
            self._copy()
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.width() / 2
        p.setPen(QPen(ThemeManager.qcolor("border-focus"), 2) if self.hasFocus() else Qt.PenStyle.NoPen)
        p.setBrush(ThemeManager.qcolor(self.role))
        p.drawEllipse(QRectF(center - 17, 2, 34, 34))
        p.setFont(ThemeManager.font("label"))
        p.setPen(ThemeManager.qcolor("text-primary"))
        p.drawText(QRectF(0, 40, self.width(), 18), Qt.AlignmentFlag.AlignCenter, self.label)
        p.setFont(ThemeManager.font("caption"))
        p.setPen(ThemeManager.qcolor("text-tertiary"))
        p.drawText(QRectF(0, 57, self.width(), 16), Qt.AlignmentFlag.AlignCenter, ThemeManager.color(self.role))
        p.end()


class GradientTile(ThemedMixin, QWidget):
    """A token gradient: click to copy its stops."""

    def __init__(self, label: str, start: str, end: str) -> None:
        super().__init__()
        self.label, self.start, self.end = label, start, end
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Click to copy the color roles")
        self.bind_theme()

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802 - Qt override
        copy_text(f"{self.start} -> {self.end}", self)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(0, 0, self.width(), 40)
        fill = QLinearGradient(box.topLeft(), box.bottomRight())
        fill.setColorAt(0, ThemeManager.qcolor(self.start))
        fill.setColorAt(1, ThemeManager.qcolor(self.end))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(fill)
        p.drawRoundedRect(box, 8, 8)
        p.setFont(ThemeManager.font("caption"))
        p.setPen(ThemeManager.qcolor("text-secondary"))
        p.drawText(QRectF(0, 43, self.width(), 16), Qt.AlignmentFlag.AlignCenter, self.label)
        p.end()


class ThemeTile(ThemedMixin, QWidget):
    """A miniature window in a theme's colors; click to apply it."""

    clicked = Signal(str)

    def __init__(self, theme: str) -> None:
        super().__init__()
        self.theme_name = theme
        self.setFixedHeight(72)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAccessibleName(f"Use {theme} theme")
        self.bind_theme()

    def mouseReleaseEvent(self, _event) -> None:  # noqa: N802 - Qt override
        self.clicked.emit(self.theme_name)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Space):
            self.clicked.emit(self.theme_name)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        colors = ThemeManager.theme(self.theme_name).colors
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        box = QRectF(1, 1, self.width() - 2, self.height() - 2)
        active = ThemeManager.current() == self.theme_name
        p.setPen(QPen(ThemeManager.qcolor("primary" if active or self.hasFocus() else "border"), 2 if active or self.hasFocus() else 1))
        p.setBrush(ThemeManager.qcolor(colors["background"][:7]))
        p.drawRoundedRect(box, 8, 8)
        p.save()
        p.setClipRect(box.adjusted(1, 1, -1, -1))
        draw_waves(p, QRectF(box.width() * .35, 0, box.width() * .65, box.height()), 4)
        p.restore()
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(ThemeManager.qcolor(colors["surface"][:7]))
        p.drawRoundedRect(QRectF(9, 12, box.width() * .4, 12), 3, 3)
        p.setBrush(ThemeManager.qcolor(colors["primary"][:7]))
        p.drawRoundedRect(QRectF(9, 30, box.width() * .24, 10), 3, 3)
        p.end()


def _row(*widgets, spacing: int = 8, stretch: bool = True) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(spacing)
    for widget in widgets:
        row.addWidget(widget)
    if stretch:
        row.addStretch(1)
    return row


class OverviewPage(QWidget):
    """The landing page of Design Studio."""

    navigate = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        content = QWidget()
        self._grid = QVBoxLayout(content)
        self._grid.setContentsMargins(12, 6, 12, 12)
        self._grid.setSpacing(SECTION_GAP)
        stacked = QWidget()
        column = QVBoxLayout(stacked)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(SECTION_GAP)
        column.addWidget(self._palette(), 3)
        column.addWidget(self._typography(), 2)
        # Each band wraps its tiles to the available width, so nothing needs horizontal scrolling.
        self._bands = [
            [(self._hero(), 53), (stacked, 34), (self._elevation(), 19)],
            [(self._buttons(), 29), (self._inputs(), 27), (self._select(), 25), (self._toggles(), 21), (self._notifications(), 25)],
            [(self._navigation(), 29), (self._display(), 36), (self._dialogs(), 37), (self._themes(), 25)],
        ]
        self._current_rows: list | None = None
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = ScrollArea(content)
        outer.addWidget(self.scroll_area)
        self._grid.addStretch(1)
        self._reflow(1320)

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        self._reflow(self.width() - 8)

    def _reflow(self, width: int) -> None:
        """Pack each band's tiles into rows that fit ``width``."""
        available = width - 24
        rows = []
        for band in self._bands:
            row, used = [], 0
            for tile, stretch in band:
                needed = max(tile.minimumSizeHint().width(), tile.minimumWidth())
                gap = SECTION_GAP if row else 0
                if row and used + gap + needed > available:
                    rows.append(row)
                    row, used, gap = [], 0, 0
                row.append((tile, stretch))
                used += gap + needed
            rows.append(row)
        shape = [[id(tile) for tile, _ in row] for row in rows]
        if shape == self._current_rows:
            return
        self._current_rows = shape
        while self._grid.count() > 1:
            old = self._grid.takeAt(0).layout()
            while old is not None and old.count():
                old.takeAt(0)
            if old is not None:
                old.setParent(None)
        for index, row in enumerate(rows):
            box = QHBoxLayout()
            box.setSpacing(SECTION_GAP)
            for tile, stretch in row:
                box.addWidget(tile, stretch)
            self._grid.insertLayout(index, box)

    # ---- top row -------------------------------------------------------------------------
    def _hero(self) -> HeroCard:
        hero = HeroCard()
        hero.setMinimumHeight(330)
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(32, 28, 32, 20)
        layout.setSpacing(10)
        accent = QFrame()
        accent.setFixedSize(44, 3)
        accent.setProperty("heroAccent", True)
        layout.addWidget(accent)
        layout.addSpacing(4)
        layout.addWidget(Text("Fluent Blue", style="display"))
        layout.addWidget(Text("A modern design system for PyQt", style="heading-3"))
        blurb = Text("Beautiful, consistent and productive UI\ncomponents for Python desktop apps.", style="body-large", color="text-secondary")
        layout.addWidget(blurb)
        layout.addSpacing(8)
        start = PrimaryButton("Get Started", size="large", icon="arrow-right", icon_position="right")
        more = Button("Learn More", size="large")
        start.setProperty("pill", "true")
        more.setProperty("pill", "true")
        start.clicked.connect(lambda: self.navigate.emit("Playground"))
        more.clicked.connect(lambda: self.navigate.emit("Foundations"))
        layout.addLayout(_row(start, more, spacing=12))
        layout.addStretch(1)
        features = QHBoxLayout()
        features.setSpacing(20)
        for icon, one, two, target in (("zap", "Modern", "Design", "Foundations"), ("grid", "Rich", "Components", "Buttons"), ("box", "Easy", "Integration", "Playground")):
            features.addWidget(self._feature(icon, one, two, target))
        features.addStretch(1)
        layout.addLayout(features)
        return hero

    def _feature(self, icon: str, one: str, two: str, target: str) -> QWidget:
        card = Button(f"{one}\n{two}", variant="ghost", icon=icon, tooltip=f"Open {target}")
        card.setProperty("feature", "true")
        card.setIconSize(QSize(22, 22))
        card.setAccessibleName(f"{one} {two}")
        card.clicked.connect(lambda: self.navigate.emit(target))
        return card

    def _palette(self) -> BentoCard:
        card = BentoCard("Color Palette", 'ThemeManager.color("primary")  # any semantic color role')
        swatches = QHBoxLayout()
        swatches.setSpacing(4)
        for label, role in (("Primary", "primary"), ("Info", "info"), ("Success", "success"), ("Warning", "warning"), ("Error", "error"), ("Neutral", "gray-400")):
            swatches.addWidget(SwatchTile(label, role))
        card.body.addLayout(swatches)
        tiles = QHBoxLayout()
        for label, start, end in (("Primary", "primary-500", "primary-300"), ("Deep", "primary-800", "primary-400"), ("Info", "info", "primary-300"), ("Success", "info", "success")):
            tiles.addWidget(GradientTile(label, start, end))
        card.body.addLayout(tiles)
        return card

    def _typography(self) -> BentoCard:
        card = BentoCard("Typography", 'Text("Heading", style="heading-1")\nThemeManager.font("body-medium")')
        row = QHBoxLayout()
        row.setSpacing(16)
        row.addWidget(Text("Aa", style="display"))
        family = QVBoxLayout()
        family.setSpacing(0)
        family.addWidget(Text("Segoe UI", style="heading-5"))
        family.addWidget(Text("Recommended, with\nnative fallbacks", style="caption", color="text-tertiary"))
        row.addLayout(family)
        row.addStretch(1)
        specs = QVBoxLayout()
        specs.setSpacing(1)
        for name, role in (("H1", "heading-1"), ("H2", "heading-2"), ("H3", "heading-3"), ("Body", "body-medium"), ("Caption", "caption")):
            spec = ThemeManager.tokens.typography[role]
            specs.addWidget(Text(f"{name}   {spec.size}px / {spec.line_height}px · {spec.weight}", style="caption", color="text-secondary"))
        row.addLayout(specs)
        card.body.addLayout(row)
        return card

    def _elevation(self) -> BentoCard:
        card = BentoCard("Elevation", "Card(elevation=2)")
        card.body.setSpacing(12)
        for level, name in ((0, "Background"), (1, "Card"), (2, "Popover"), (3, "Modal")):
            tile = Card(elevation=level, clickable=True)
            tile.setToolTip(f"Copy Card(elevation={level})")
            layout = tile.content_layout()
            layout.setContentsMargins(12, 7, 12, 7)
            layout.setSpacing(0)
            layout.addWidget(Text(f"Level {level}", style="heading-6"))
            layout.addWidget(Text(name, style="caption", color="text-tertiary"))
            tile.clicked.connect(lambda n=level: copy_text(f"Card(elevation={n})", tile))
            card.body.addWidget(tile)
        card.body.addStretch(1)
        return card

    # ---- middle row ------------------------------------------------------------------------
    def _buttons(self) -> BentoCard:
        card = BentoCard("Buttons", 'Button("Save", variant="primary", size="large", icon="download")')
        items = ["Duplicate", "Archive", None, {"text": "Delete", "icon": "trash", "danger": True}]
        rows = [("Primary", "primary"), ("Secondary", "secondary"), ("Outline", "outline"), ("Text", "text")]
        for label, variant in rows:
            main = Button(label, variant=variant, size="small")
            main.clicked.connect(lambda _=False, b=main, t=label: Toast.show(f"{t} button clicked", parent=b, duration=1400))
            card.body.addLayout(_row(main, DropdownMenu(label, items=items, variant=variant, size="small"),
                                     Button("Icon", variant=variant, size="small", icon="download", icon_position="right"), spacing=6))
        large = PrimaryButton("Large")

        def busy() -> None:
            large.set_loading(True)
            QTimer.singleShot(1200, lambda: large.set_loading(False))

        large.clicked.connect(busy)
        star = IconButton("settings", variant="secondary", size="small", tooltip="Settings")
        star.clicked.connect(lambda: self.navigate.emit("Themes"))
        card.body.addLayout(_row(Button("Small", size="small"), Button("Default", size="small"), large, IconButton("search", size="small", tooltip="Search"),
                                 star, IconButton("plus", variant="primary", size="small", tooltip="Add"), spacing=4))
        card.body.addStretch(1)
        return card

    @staticmethod
    def _compact(combo):
        combo.setMinimumContentsLength(3)
        return combo

    def _inputs(self) -> BentoCard:
        card = BentoCard("Inputs", 'Input(placeholder="Please input…", clearable=True, validation="error")')
        columns = QHBoxLayout()
        columns.setSpacing(10)
        left = QVBoxLayout()
        left.setSpacing(4)
        for label, widget in (("Input Label", Input(placeholder="Please input…", clearable=True)),
                              ("Select Label", self._compact(ComboBox(["Design", "Engineering"], placeholder="Please select…"))),
                              ("Search", SearchInput())):
            left.addWidget(Text(label, style="label"))
            left.addWidget(widget)
            left.addSpacing(4)
        left.addWidget(Input("Disabled Input", disabled=True))
        left.addStretch(1)
        right = QVBoxLayout()
        right.setSpacing(6)
        right.addWidget(Text("Input States", style="label"))
        for text, prop, validation, icon in (("Normal", None, "none", None), ("Hover", "hover", "none", None), ("Focus", "focus", "none", None),
                                             ("Error", None, "error", "alert-circle"), ("Success", None, "success", "check-circle")):
            field = Input(text, validation=validation, suffix_icon=icon)
            field.setMinimumWidth(106)
            if prop:
                field.setProperty("specimen", prop)
            right.addWidget(field)
        right.addStretch(1)
        columns.addLayout(left, 5)
        columns.addLayout(right, 4)
        card.body.addLayout(columns)
        return card

    def _select(self) -> BentoCard:
        card = BentoCard("Select & Dropdown", 'Select(["Option 1", "Option 2"], value="Option 1")')
        options = [f"Option {n}" for n in range(1, 5)]
        select = Select(options, value="Option 1")
        card.body.addWidget(select)
        listing = QListWidget()
        listing.setAccessibleName("Options")
        listing.setFixedHeight(4 * 28 + 4)
        for option in options:
            listing.addItem(QListWidgetItem(option))
        listing.setCurrentRow(0)
        listing.currentRowChanged.connect(lambda row: select.setCurrentIndex(row) if row >= 0 else None)
        select.currentIndexChanged.connect(listing.setCurrentRow)
        card.body.addWidget(listing)
        card.body.addWidget(SegmentedControl(["Option 1", "Option 2", "Option 3"]))
        more = Button("More", icon="chevron-right", icon_position="right", size="small")
        more.clicked.connect(lambda: self.navigate.emit("Selection"))
        card.body.addLayout(_row(DropdownMenu("Dropdown", items=options, size="small"), more))
        card.body.addStretch(1)
        return card

    def _toggles(self) -> BentoCard:
        card = BentoCard("Switch & Checkbox", 'Switch("On", checked=True)\nCheckbox("Accept", checked=True)')
        on, off = Switch("On", checked=True), Switch("Off")
        on.toggled.connect(lambda v: on.setText("On" if v else "Off"))
        off.toggled.connect(lambda v: off.setText("On" if v else "Off"))
        for widget in (on, off, Checkbox("Checkbox", checked=True), Checkbox("Checkbox")):
            card.body.addWidget(widget)
        group = RadioGroup(["Radio", "Radio 2"], value="Radio")
        group.layout().setSpacing(6)
        card.body.addWidget(group)
        card.body.addWidget(Switch("Switch", checked=True))
        card.body.addStretch(1)
        return card

    def _notifications(self) -> BentoCard:
        card = BentoCard("Notifications", 'Toast.show("Saved!", parent=window, variant="success")')
        card.setMinimumWidth(208)  # Keeps each message to at most three lines.
        holder = QVBoxLayout()
        holder.setSpacing(6)
        card.body.addLayout(holder)
        restore = TextButton("Show all again", icon="refresh", size="small")
        card.body.addWidget(restore)
        restore.hide()
        state: list = []

        def fill() -> None:
            restore.hide()
            state.clear()
            for widget in (Alert(message="This is an informational message.", variant="info", closable=True, dense=True),
                           Alert(message="Operation completed successfully!", variant="success", closable=True, dense=True),
                           Alert(message="Please check your input.", variant="warning", closable=True, dense=True),
                           Alert(message="An error occurred.", variant="error", closable=True, dense=True)):
                holder.addWidget(widget)
                state.append(widget)
                widget.closed.connect(lambda w=widget: closed(w))
            saved = ToastCard(message="Saved!", variant="success", duration=0)
            saved.message_label.setMinimumWidth(60)
            saved.closed.connect(lambda w=saved: closed(w))
            holder.addWidget(saved, 0, Qt.AlignmentFlag.AlignRight)
            state.append(saved)

        def closed(widget) -> None:
            state.remove(widget)
            holder.removeWidget(widget)
            widget.deleteLater()
            if not state:
                restore.show()

        restore.clicked.connect(fill)
        fill()
        card.body.addStretch(1)
        return card

    # ---- bottom row ------------------------------------------------------------------------
    def _navigation(self) -> BentoCard:
        card = BentoCard("Navigation", 'sidebar = Sidebar()\nsidebar.add_item("Home", icon="home")')
        row = QHBoxLayout()
        row.setSpacing(10)
        side = Sidebar(width=116)
        side.setProperty("embedded", True)
        side.header_layout.setContentsMargins(0, 0, 0, 0)
        side.footer_layout.setContentsMargins(0, 0, 0, 0)
        names = (("Home", "home"), ("Projects", "folder"), ("Analytics", "chart-bar"), ("Settings", "settings"), ("About", "info-circle"))
        for name, icon in names:
            side.add_item(name, icon=icon)
        row.addWidget(side)
        right = QVBoxLayout()
        crumb = Breadcrumb(["Home", "Dashboard"])
        side.current_changed.connect(lambda key: crumb.set_items(["Home", key] if key != "Home" else ["Home", "Dashboard"]))
        right.addWidget(crumb)
        tabs = Tabs()
        tabs.setMinimumWidth(190)
        for number in (1, 2, 3):
            tabs.add_tab(Text(f"Content of tab {number}", color="text-secondary"), f"Tab {number}")
        right.addWidget(tabs, 1)
        star = IconButton("star", size="small", tooltip="Favorite", checkable=True)
        right.addLayout(_row(DropdownMenu("Item", items=["First", "Second"], size="small", variant="ghost"), star, IconButton("search", size="small", tooltip="Search"), spacing=4))
        row.addLayout(right, 1)
        card.body.addLayout(row)
        return card

    def _display(self) -> BentoCard:
        card = BentoCard("Data Display", 'ListItem("Alice Johnson", subtitle="Online", leading=Avatar("Alice Johnson", status="online"))')
        row = QHBoxLayout()
        row.setSpacing(12)
        story = Card()
        layout = story.content_layout()
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(2)
        art = LandscapeArt()
        art.setFixedHeight(64)
        art.setMinimumWidth(150)
        layout.addWidget(art)
        for widget in (Text("Beautiful Landscape", style="heading-6"), Text("A peaceful view of nature.", style="caption", color="text-secondary")):
            widget.setContentsMargins(10, 2, 10, 0)
            layout.addWidget(widget)
        read = TextButton("Read More", icon="arrow-right", icon_position="right", size="small")
        read.setContentsMargins(8, 0, 0, 0)
        details = Popover(read, title="Beautiful Landscape", content="This picture is generated from theme tokens with QPainter, so it follows the active theme.")
        read.clicked.connect(lambda: details.show_at(read))
        layout.addWidget(read)
        row.addWidget(story, 1)
        people = QVBoxLayout()
        people.setSpacing(0)
        people.addWidget(Text("List", style="heading-6"))
        entries = []

        def pick(chosen) -> None:
            for entry in entries:
                entry.set_selected(entry is chosen)

        for name, note, status in (("Alice Johnson", "Online", "online"), ("Bob Smith", "2m ago", "away"), ("Charlie Brown", "1h ago", "offline")):
            item = ListItem(name, subtitle=note, leading=Avatar(name, status=status), clickable=True)
            item.clicked.connect(lambda i=item: pick(i))
            entries.append(item)
            people.addWidget(item)
        people.addStretch(1)
        row.addLayout(people, 1)
        card.body.addLayout(row)
        return card

    def _dialogs(self) -> BentoCard:
        card = BentoCard("Dialogs & Overlays", 'ConfirmDialog.ask(window, "Confirm Action", "Are you sure?")')
        row = QHBoxLayout()
        row.setSpacing(16)
        panel = Card(elevation=2)
        layout = panel.content_layout()
        layout.setContentsMargins(14, 12, 14, 12)
        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(icon_pixmap("info-circle", 18, "primary-text"))
        head.addWidget(icon)
        head.addWidget(Text("Confirm Action", style="heading-5"), 1)
        layout.addLayout(head)
        layout.addWidget(Text("Are you sure you want to continue?", style="body-small", color="text-secondary", wrap=True))
        cancel = Button("Cancel", size="small")
        confirm = PrimaryButton("OK", size="small")
        cancel.clicked.connect(lambda: Toast.show("Cancelled", parent=panel, duration=1400))

        def open_dialog() -> None:
            dialog = ConfirmDialog(panel, title="Confirm Action", message="Are you sure you want to continue?")
            dialog.confirmed.connect(lambda: Toast.show("Confirmed", parent=panel, variant="success", duration=1400))
            dialog.open()

        confirm.clicked.connect(open_dialog)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)
        layout.addStretch(1)
        layout.addLayout(buttons)
        row.addWidget(panel, 3)
        progress = QVBoxLayout()
        progress.setSpacing(6)
        progress.addWidget(Text("Progress", style="heading-6"))
        ring = CircularProgress(75, size=72, thickness=6)
        bar = ProgressBar(75)
        slider = Slider(75)
        slider.setAccessibleName("Progress value")
        slider.valueChanged.connect(ring.set_value)
        slider.valueChanged.connect(bar.set_value)
        progress.addWidget(ring, 0, Qt.AlignmentFlag.AlignHCenter)
        progress.addWidget(bar)
        progress.addWidget(slider)
        progress.addStretch(1)
        row.addLayout(progress, 2)
        card.body.addLayout(row)
        return card

    def _themes(self) -> BentoCard:
        card = BentoCard("Themes", 'ThemeManager.set_theme("dark")')
        tiles = QHBoxLayout()
        radios = QHBoxLayout()
        group = QButtonGroup(card)
        self._theme_radios = {}
        for name, label in (("light", "Light"), ("dark", "Dark")):
            column = QVBoxLayout()
            tile = ThemeTile(name)
            radio = RadioButton(label, checked=ThemeManager.current() == name)
            group.addButton(radio)
            self._theme_radios[name] = radio
            tile.clicked.connect(self._apply_theme)
            radio.clicked.connect(lambda _=False, n=name: self._apply_theme(n))
            column.addWidget(tile)
            column.addWidget(radio)
            tiles.addLayout(column)
        card.body.addLayout(tiles)
        auto = Switch("Auto Switch")
        follow = Select([("Follow System", "system"), ("Always Light", "light"), ("Always Dark", "dark")], value="system", size="small")
        follow.setMinimumWidth(146)
        follow.setEnabled(False)

        def apply_auto() -> None:
            follow.setEnabled(auto.isChecked())
            if auto.isChecked():
                self._apply_theme(follow.value())

        auto.toggled.connect(lambda _on: apply_auto())
        follow.value_changed.connect(lambda _v: apply_auto())
        card.body.addLayout(_row(auto, follow))
        card.body.addStretch(1)
        ThemeManager.theme_changed.connect(self._sync_theme)
        return card

    def _apply_theme(self, name: str) -> None:
        ThemeManager.set_theme(name)

    def _sync_theme(self, name: str) -> None:
        radio = self._theme_radios.get(name)
        if radio:
            radio.setChecked(True)


