"""ImageViewer, TreeView, FileTree, Stepper and Wizard."""
from __future__ import annotations

from ...compatibility.qt import (
    QFileIconProvider,
    QFileSystemModel,
    QFrame,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QPainter,
    QPen,
    QPixmap,
    QRectF,
    QSize,
    QSizePolicy,
    QSortFilterProxyModel,
    QStackedWidget,
    QStandardItem,
    QStandardItemModel,
    Qt,
    QTreeView,
    QVBoxLayout,
    QWidget,
    Signal,
)
from ...core.theme_manager import ThemeManager
from ...icons import icon as make_icon
from ...icons import icon_pixmap
from ..base import ThemedMixin
from ..buttons.button import Button, IconButton
from ..display.text import Text

_ID_ROLE = Qt.ItemDataRole.UserRole + 10
_ICON_ROLE = Qt.ItemDataRole.UserRole + 11


class _GraphicsView(QGraphicsView):
    def __init__(self, viewer) -> None:
        super().__init__()
        self.viewer = viewer
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setFrameShape(QFrame.Shape.NoFrame)

    def wheelEvent(self, event) -> None:  # noqa: N802 - Qt override
        self.viewer.zoom_by(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)


class ImageViewer(ThemedMixin, QFrame):
    """An image viewer with zoom, pan, rotate and fit.

    Args:
        image: Path or ``QPixmap``.
        min_zoom: Lowest zoom factor.
        max_zoom: Highest zoom factor.

    Signals:
        zoom_changed(float): The new zoom factor.
    """

    zoom_changed = Signal(float)

    def __init__(self, image=None, parent=None, *, min_zoom: float = .05, max_zoom: float = 16.0) -> None:
        super().__init__(parent)
        self._min, self._max = min_zoom, max_zoom
        self._zoom, self._rotation = 1.0, 0
        self._fit = True
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        bar = QHBoxLayout()
        bar.setContentsMargins(6, 6, 6, 6)
        bar.setSpacing(2)
        for icon, tip, handler in (("zoom-out", "Zoom out", lambda: self.zoom_by(1 / 1.25)),
                                   ("zoom-in", "Zoom in", lambda: self.zoom_by(1.25)),
                                   ("maximize", "Fit to view", self.fit),
                                   ("rotate", "Rotate", self.rotate)):
            button = IconButton(icon, size="small", tooltip=tip)
            button.clicked.connect(lambda _=False, h=handler: h())
            bar.addWidget(button)
        actual = Button("100%", size="small", variant="ghost", tooltip="Actual size")
        actual.clicked.connect(lambda: self.set_zoom(1.0))
        bar.addWidget(actual)
        bar.addStretch(1)
        self.zoom_label = Text("", style="body-small", color="text-tertiary")
        bar.addWidget(self.zoom_label)
        layout.addLayout(bar)
        self.scene = QGraphicsScene(self)
        self.item = QGraphicsPixmapItem()
        self.item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.scene.addItem(self.item)
        self.view = _GraphicsView(self)
        self.view.setScene(self.scene)
        self.view.setAccessibleName("Image")
        layout.addWidget(self.view, 1)
        self.bind_theme()
        if image is not None:
            self.set_image(image)

    def set_image(self, image) -> bool:
        """Load an image from a path or ``QPixmap``. Returns ``False`` if it could not load."""
        pixmap = QPixmap(str(image)) if not isinstance(image, QPixmap) else image
        if pixmap.isNull():
            self.item.setPixmap(QPixmap())
            return False
        self.item.setPixmap(pixmap)
        self.item.setTransformOriginPoint(self.item.boundingRect().center())
        self._rotation = 0
        self.item.setRotation(0)
        self.scene.setSceneRect(self.item.sceneBoundingRect())
        self.fit()
        return True

    def has_image(self) -> bool:
        return not self.item.pixmap().isNull()

    def zoom(self) -> float:
        return self._zoom

    def set_zoom(self, zoom: float) -> None:
        """Set an absolute zoom factor, clamped to the limits."""
        self._fit = False
        self._set_scrollbars(True)
        self.view.resetTransform()
        self._apply_zoom(min(self._max, max(self._min, zoom)))
        self.view.scale(self._zoom, self._zoom)

    def zoom_by(self, factor: float) -> None:
        """Multiply the current zoom."""
        self.set_zoom(self._zoom * factor)

    def fit(self) -> None:
        """Scale the image to fit the view."""
        self._fit = True
        self._set_scrollbars(False)
        if not self.has_image():
            return
        self.view.fitInView(self.item, Qt.AspectRatioMode.KeepAspectRatio)
        self._apply_zoom(self.view.transform().m11() or 1.0)

    def rotate(self, degrees: int = 90) -> None:
        """Rotate clockwise."""
        self._rotation = (self._rotation + degrees) % 360
        self.item.setRotation(self._rotation)
        self.scene.setSceneRect(self.item.sceneBoundingRect())
        if self._fit:
            self.fit()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt override
        super().resizeEvent(event)
        if self._fit:
            self.fit()

    def _set_scrollbars(self, on: bool) -> None:
        policy = Qt.ScrollBarPolicy.ScrollBarAsNeeded if on else Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        self.view.setHorizontalScrollBarPolicy(policy)
        self.view.setVerticalScrollBarPolicy(policy)

    def _apply_zoom(self, zoom: float) -> None:
        changed = abs(zoom - self._zoom) > 1e-6
        self._zoom = zoom
        self.zoom_label.setText(f"{round(zoom * 100)}%")
        if changed:
            self.zoom_changed.emit(zoom)


class TreeView(ThemedMixin, QTreeView):
    """A tree from nested dicts, with built-in filtering.

    Args:
        items: Dicts with ``text`` and optional ``id``, ``icon`` and ``children``.
        expand_all: Expand every node initially.

    Signals:
        item_selected(object): The id of the current item.
        item_activated(object): The id of an item activated by double-click or Enter.
    """

    item_selected = Signal(object)
    item_activated = Signal(object)

    def __init__(self, items=None, parent=None, *, expand_all: bool = True) -> None:
        super().__init__(parent)
        self._expand_all = expand_all
        self._source = QStandardItemModel(self)
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._source)
        self._proxy.setRecursiveFilteringEnabled(True)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setModel(self._proxy)
        self.setHeaderHidden(True)
        self.setIconSize(QSize(16, 16))
        self.setIndentation(18)
        self.setUniformRowHeights(True)
        self.setAccessibleName("Tree")
        self.setEditTriggers(QTreeView.EditTrigger.NoEditTriggers)
        self.selectionModel().currentChanged.connect(lambda current, _prev: self.item_selected.emit(current.data(_ID_ROLE)) if current.isValid() else None)
        self.activated.connect(lambda index: self.item_activated.emit(index.data(_ID_ROLE)))
        self.bind_theme()
        self.set_items(items or [])

    def set_items(self, items) -> None:
        """Replace the tree."""
        self._source.clear()
        for item in items:
            self._source.appendRow(self._build(item))
        if self._expand_all:
            self.expandAll()

    def set_filter(self, text: str) -> None:
        """Show only matching items and their ancestors."""
        self._proxy.setFilterFixedString(text)
        if text or self._expand_all:
            self.expandAll()

    def visible_count(self) -> int:
        """Visible items, counting expanded and collapsed descendants."""
        def count(parent) -> int:
            rows = self._proxy.rowCount(parent)
            return rows + sum(count(self._proxy.index(i, 0, parent)) for i in range(rows))
        return count(self.rootIndex())

    def current_id(self):
        index = self.currentIndex()
        return index.data(_ID_ROLE) if index.isValid() else None

    def refresh_theme(self) -> None:
        def walk(parent) -> None:
            for row in range(parent.rowCount()):
                child = parent.child(row)
                name = child.data(_ICON_ROLE)
                if name:
                    child.setIcon(make_icon(name, 16, "text-secondary"))
                walk(child)
        walk(self._source.invisibleRootItem())

    def _build(self, spec: dict) -> QStandardItem:
        item = QStandardItem(spec["text"])
        item.setData(spec.get("id", spec["text"]), _ID_ROLE)
        if spec.get("icon"):
            item.setData(spec["icon"], _ICON_ROLE)
            item.setIcon(make_icon(spec["icon"], 16, "text-secondary"))
        for child in spec.get("children", []):
            item.appendRow(self._build(child))
        return item


class _ThemedIcons(QFileIconProvider):
    def icon(self, target):  # noqa: D102
        if isinstance(target, QFileIconProvider.IconType):
            return make_icon("folder" if target == QFileIconProvider.IconType.Folder else "file", 16, "text-secondary")
        if target.isDir():
            return make_icon("folder", 16, "primary-text")
        code = {"py", "json", "js", "ts", "html", "css", "toml", "yaml", "yml", "sh", "c", "cpp", "rs"}
        images = {"png", "jpg", "jpeg", "gif", "svg", "webp"}
        suffix = target.suffix().lower()
        name = "file-code" if suffix in code else "image" if suffix in images else "file-text" if suffix in {"md", "txt"} else "file"
        return make_icon(name, 16, "text-secondary")


class FileTree(ThemedMixin, QTreeView):
    """A lazily loaded file system tree, using ``QFileSystemModel``.

    Args:
        root: Root directory.
        name_filters: Patterns such as ``["*.py"]``; others are hidden.

    Signals:
        file_selected(str): The path of the current item.
        file_activated(str): The path of a file activated by double-click or Enter.
    """

    file_selected = Signal(str)
    file_activated = Signal(str)

    def __init__(self, root: str = "", parent=None, *, name_filters=None) -> None:
        super().__init__(parent)
        self.fs = QFileSystemModel(self)
        self._icons = _ThemedIcons()
        self.fs.setIconProvider(self._icons)
        if name_filters:
            self.fs.setNameFilters(list(name_filters))
            self.fs.setNameFilterDisables(False)
        self.setModel(self.fs)
        self.setHeaderHidden(True)
        self.setAnimated(False)
        self.setIconSize(QSize(16, 16))
        self.setIndentation(18)
        self.setUniformRowHeights(True)
        self.setAccessibleName("File tree")
        for column in range(1, self.fs.columnCount()):
            self.hideColumn(column)
        self.selectionModel().currentChanged.connect(lambda current, _prev: self.file_selected.emit(self.fs.filePath(current)) if current.isValid() else None)
        self.activated.connect(self._on_activated)
        self.bind_theme()
        if root:
            self.set_root(root)

    def set_root(self, path: str) -> None:
        """Show a directory as the root."""
        self.setRootIndex(self.fs.setRootPath(str(path)))

    def root(self) -> str:
        return self.fs.rootPath()

    def current_path(self) -> str:
        index = self.currentIndex()
        return self.fs.filePath(index) if index.isValid() else ""

    def refresh_theme(self) -> None:
        self.viewport().update()

    def _on_activated(self, index) -> None:
        if self.fs.isDir(index):
            self.setExpanded(index, not self.isExpanded(index))
        else:
            self.file_activated.emit(self.fs.filePath(index))


class Stepper(ThemedMixin, QWidget):
    """Shows progress through ordered steps. Arrow keys move when ``clickable``.

    Args:
        steps: Step titles.
        current: Current 0-based step.
        clickable: Allow moving to completed steps by mouse and keyboard.

    Signals:
        current_changed(int): The current step changed.
        step_clicked(int): A step was chosen by the user.
    """

    current_changed = Signal(int)
    step_clicked = Signal(int)
    _NODE = 26

    def __init__(self, steps=None, parent=None, *, current: int = 0, clickable: bool = False) -> None:
        super().__init__(parent)
        self._steps = list(steps or [])
        self._current, self._clickable = current, clickable
        self._errors: set[int] = set()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus if clickable else Qt.FocusPolicy.NoFocus)
        self._sync_accessible()
        self.bind_theme()

    def current(self) -> int:
        return self._current

    def steps(self) -> list[str]:
        return list(self._steps)

    def set_current(self, index: int) -> None:
        """Move to a step, clamped to the range."""
        index = min(max(0, index), max(0, len(self._steps) - 1))
        if index != self._current:
            self._current = index
            self._sync_accessible()
            self.update()
            self.current_changed.emit(index)

    def set_error(self, index: int, error: bool = True) -> None:
        """Mark a step as failed."""
        self._errors.add(index) if error else self._errors.discard(index)
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802 - Qt override
        return QSize(max(1, len(self._steps)) * 120, self._NODE + 6)

    def _slots(self) -> list[QRectF]:
        count = max(1, len(self._steps))
        width = self.width() / count
        return [QRectF(i * width, 0, width, self.height()) for i in range(count)]

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 - Qt override
        if not self._clickable:
            return
        for index, slot in enumerate(self._slots()):
            if slot.contains(event.position()) and index <= self._current:
                self.step_clicked.emit(index)
                self.set_current(index)

    def keyPressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._clickable and event.key() == Qt.Key.Key_Left and self._current > 0:
            self.step_clicked.emit(self._current - 1)
            self.set_current(self._current - 1)
        else:
            super().keyPressEvent(event)

    def _sync_accessible(self) -> None:
        if self._steps:
            title = self._steps[min(self._current, len(self._steps) - 1)]
            self.setAccessibleName(f"Step {self._current + 1} of {len(self._steps)}: {title}")

    def paintEvent(self, _event) -> None:  # noqa: N802 - Qt override
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        node = self._NODE
        y = (self.height() - node) / 2
        fm_font = ThemeManager.font("body-small")
        painter.setFont(fm_font)
        slots = self._slots()
        for index, title in enumerate(self._steps):
            slot = slots[index]
            circle = QRectF(slot.left() + 2, y, node, node)
            error, done, active = index in self._errors, index < self._current, index == self._current
            if index < len(self._steps) - 1:
                advance = painter.fontMetrics().horizontalAdvance(title)
                x1 = min(circle.right() + 8 + advance + 10, slot.right() - 4)
                painter.setPen(QPen(ThemeManager.qcolor("primary" if done else "border"), 2))
                painter.drawLine(int(x1), int(self.height() / 2), int(slot.right()), int(self.height() / 2))
            fill = "error" if error else "primary" if done or active else "surface-tertiary"
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(ThemeManager.qcolor(fill))
            painter.drawEllipse(circle)
            if error or done:
                pixmap = icon_pixmap("close" if error else "check", 14, "on-primary")
                painter.drawPixmap(int(circle.left() + 6), int(circle.top() + 6), pixmap)
            else:
                painter.setPen(ThemeManager.qcolor("on-primary" if active else "text-secondary"))
                painter.drawText(circle, Qt.AlignmentFlag.AlignCenter, str(index + 1))
            label = "error-text" if error else "text-primary" if active or done else "text-tertiary"
            painter.setFont(ThemeManager.font("heading-6") if active else fm_font)
            painter.setPen(ThemeManager.qcolor(label))
            text_rect = QRectF(circle.right() + 8, 0, slot.right() - circle.right() - 8, self.height())
            elided = painter.fontMetrics().elidedText(title, Qt.TextElideMode.ElideRight, int(text_rect.width()))
            painter.drawText(text_rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), elided)
            painter.setFont(fm_font)
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(ThemeManager.qcolor("border-focus"), 1))
            painter.drawRoundedRect(QRectF(self.rect()).adjusted(.5, .5, -.5, -.5), 4, 4)
        painter.end()


class Wizard(QFrame):
    """A multi-step flow with a stepper, validation and navigation.

    Args:
        finish_text: Label of the last step's button.
        cancelable: Show a cancel button.

    Signals:
        page_changed(int): The current page changed.
        finished: The last page was completed.
        cancelled: The cancel button was used.
    """

    page_changed = Signal(int)
    finished = Signal()
    cancelled = Signal()

    def __init__(self, parent=None, *, finish_text: str = "Finish", cancelable: bool = False) -> None:
        super().__init__(parent)
        ThemeManager.ensure_applied()
        self._finish_text = finish_text
        self._validators: list = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        self.stepper = Stepper(clickable=True)
        self.stepper.step_clicked.connect(self._go)
        layout.addWidget(self.stepper)
        self.pages = QStackedWidget()
        layout.addWidget(self.pages, 1)
        footer = QHBoxLayout()
        footer.setSpacing(8)
        if cancelable:
            cancel = Button("Cancel", variant="ghost")
            cancel.clicked.connect(lambda: self.cancelled.emit())
            footer.addWidget(cancel)
        footer.addStretch(1)
        self.back_button = Button("Back", icon="arrow-left")
        self.next_button = Button("Next", variant="primary", icon="arrow-right", icon_position="right")
        self.back_button.clicked.connect(self.back)
        self.next_button.clicked.connect(self.next)
        footer.addWidget(self.back_button)
        footer.addWidget(self.next_button)
        layout.addLayout(footer)
        self._sync()

    def add_page(self, title: str, widget, validator=None) -> int:
        """Add a step.

        Args:
            title: Step title.
            widget: Page content.
            validator: Optional ``callable() -> bool``; returning ``False`` blocks Next.
        """
        self._validators.append(validator)
        self.stepper._steps.append(title)
        self.stepper.updateGeometry()
        self.stepper.update()
        index = self.pages.addWidget(widget)
        self._sync()
        return index

    def current(self) -> int:
        return self.pages.currentIndex()

    def next(self) -> bool:
        """Validate and advance, finishing on the last page. Returns ``False`` if blocked."""
        index = self.current()
        validator = self._validators[index] if 0 <= index < len(self._validators) else None
        if validator and not validator():
            self.stepper.set_error(index)
            return False
        self.stepper.set_error(index, False)
        if index >= self.pages.count() - 1:
            self.finished.emit()
            return True
        self._go(index + 1)
        return True

    def back(self) -> None:
        """Return to the previous page."""
        if self.current() > 0:
            self._go(self.current() - 1)

    def _go(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        self.stepper.set_current(index)
        self._sync()
        self.page_changed.emit(index)

    def _sync(self) -> None:
        index, count = self.current(), self.pages.count()
        self.back_button.setEnabled(index > 0)
        last = index >= count - 1
        self.next_button.setText(self._finish_text if last else "Next")
        self.next_button.set_icon("check" if last else "arrow-right")
