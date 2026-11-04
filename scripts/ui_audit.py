"""Measure every Design Studio page for UI defects. Exit status 1 if any defect is found.

Checks: clipped text in buttons, labels, inputs and combo boxes; wrapped labels shorter than
their text; widgets squeezed below their minimum; siblings in a layout that overlap; children
outside a parent that does not scroll; and low text contrast measured from rendered pixels.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fluent_blue import ThemeManager  # noqa: E402
from fluent_blue.compatibility.qt import (  # noqa: E402
    QAbstractButton, QAbstractScrollArea, QApplication, QComboBox, QLabel, QLineEdit, QStackedWidget, Qt, QTabWidget, QWidget,
)
from fluent_blue.core.palette import contrast_ratio  # noqa: E402
from fluent_blue.studio.app import StudioWindow  # noqa: E402

SIZES = ((1536, 1024), (1366, 768), (1024, 680))
PAGES = ("Overview", "Foundations", "Colors", "Typography", "Icons", "Buttons", "Inputs", "Selection", "Navigation", "Data Display",
         "Feedback", "Data Tables", "Layout", "Advanced Components", "Themes", "Playground", "About", "Changelog")


def describe(widget) -> str:
    path, node = [], widget
    while node is not None and len(path) < 4:
        path.append(type(node).__name__)
        node = node.parentWidget()
    return "<".join(path)


def inside_scroller(widget) -> bool:
    node = widget.parentWidget()
    while node is not None:
        if isinstance(node, QAbstractScrollArea):
            return True
        node = node.parentWidget()
    return False


def text_of(widget) -> str:
    return widget.text() if hasattr(widget, "text") and callable(widget.text) else ""


def check_widget(widget, report) -> None:
    if widget.width() <= 0 or widget.height() <= 0:
        return
    metrics = widget.fontMetrics()
    if isinstance(widget, QAbstractButton) and widget.text() and not isinstance(widget.parentWidget(), QLineEdit):
        lines = widget.text().split("\n")
        needed = max(metrics.horizontalAdvance(line) for line in lines)
        if not widget.icon().isNull():
            needed += widget.iconSize().width() + 2
        if needed + 2 > widget.width():
            report("button-clip", widget, f"{widget.text()!r} needs {needed}px, has {widget.width()}px")
        if metrics.height() * len(lines) > widget.height():
            report("button-clip-v", widget, f"{widget.text()!r} height {widget.height()}")
    elif isinstance(widget, QLabel) and widget.text() and widget.pixmap().isNull():
        if widget.wordWrap():
            needed = widget.heightForWidth(widget.width())
            if needed > widget.height():
                report("label-wrap-clip", widget, f"{widget.text()[:40]!r} needs {needed}px high, has {widget.height()}px")
        else:
            hint = widget.minimumSizeHint()
            if hint.width() > widget.width() + 1:
                report("label-clip", widget, f"{widget.text()[:40]!r} needs {hint.width()}px, has {widget.width()}px")
            if metrics.height() > widget.height() + 1:
                report("label-clip-v", widget, f"{widget.text()[:40]!r} line {metrics.height()}px, has {widget.height()}px")
    elif isinstance(widget, QLineEdit) and widget.text():
        reserved = 22 + sum(30 for a in widget.actions() if a.isVisible())
        needed = metrics.horizontalAdvance(widget.displayText())
        if needed + reserved > widget.width():
            report("input-clip", widget, f"{widget.text()[:30]!r} needs {needed + reserved}px, has {widget.width()}px")
    elif isinstance(widget, QComboBox) and not widget.isEditable() and widget.currentText():
        needed = metrics.horizontalAdvance(widget.currentText()) + 56
        if needed > widget.width():
            report("combo-clip", widget, f"{widget.currentText()!r} needs {needed}px, has {widget.width()}px")
    hint = widget.minimumSizeHint()
    in_view = isinstance(widget.parentWidget(), QAbstractScrollArea)  # Viewports and gutters follow their view.
    if hint.isValid() and not in_view and widget.minimumWidth() == 0 and not isinstance(widget, (QLabel, QAbstractScrollArea)) and widget.layout() is not None:
        if hint.height() > widget.height() + 1 and not widget.layout().hasHeightForWidth():
            report("squeezed", widget, f"height {widget.height()} < minimum {hint.height()}")
        if hint.width() > widget.width() + 1:
            report("squeezed", widget, f"width {widget.width()} < minimum {hint.width()}")


def check_children(widget, report) -> None:
    if isinstance(widget, (QAbstractScrollArea, QStackedWidget, QTabWidget)):
        return
    layout = widget.layout()
    if layout is None:
        return
    items = []
    def collect(lay):
        for i in range(lay.count()):
            item = lay.itemAt(i)
            if item.widget() is not None and item.widget().isVisible():
                items.append(item.widget())
            elif item.layout() is not None:
                collect(item.layout())
    collect(layout)
    for index, first in enumerate(items):
        if not widget.rect().adjusted(-1, -1, 1, 1).contains(first.geometry()) and first.parentWidget() is widget:
            report("overflow", first, f"{first.geometry().getRect()} outside parent {widget.width()}x{widget.height()}")
        for second in items[index + 1:]:
            if first.parentWidget() is second.parentWidget():
                overlap = first.geometry().intersected(second.geometry())
                if overlap.width() > 1 and overlap.height() > 1 and getattr(widget, "_fb_overlap_ok", False) is False:
                    report("overlap", first, f"overlaps {type(second).__name__} by {overlap.width()}x{overlap.height()}")


def fully_visible(widget) -> bool:
    return widget.visibleRegion().boundingRect().size() == widget.size()


def check_contrast(widget, image, ratio, report) -> None:
    """Compare the strongest ink in a text widget with the background rendered behind it."""
    if not isinstance(widget, (QLabel, QAbstractButton)) or not text_of(widget) or not widget.isEnabled() or not fully_visible(widget):
        return
    if isinstance(widget.parentWidget(), QLineEdit) or len(text_of(widget).strip()) < 3:
        return  # Antialiasing stops one or two tiny glyphs from reaching their true color.
    if isinstance(widget, QLabel) and not widget.pixmap().isNull():
        return
    origin = widget.mapTo(widget.window(), widget.rect().topLeft())
    # Sample a central band, every pixel, to catch thin glyph strokes and skip borders.
    x0, y0 = round((origin.x() + 3) * ratio), round((origin.y() + 3) * ratio)
    x1, y1 = round((origin.x() + widget.width() - 3) * ratio), round((origin.y() + widget.height() - 3) * ratio)
    counts: dict[str, int] = {}
    for py in range(max(0, y0), min(y1, image.height())):
        for px in range(max(0, x0), min(x1, image.width())):
            color = image.pixelColor(px, py).name()
            counts[color] = counts.get(color, 0) + 1
    if len(counts) < 2:
        return
    background = max(counts, key=counts.get)
    foreground = max(counts, key=lambda c: contrast_ratio(c, background))
    value = contrast_ratio(foreground, background)
    large = widget.font().pixelSize() >= 18 or (widget.font().pixelSize() >= 14 and widget.font().bold())
    if value < (3.0 if large else 4.5):
        report("contrast", widget, f"{text_of(widget)[:30]!r} {foreground} on {background} = {value:.2f}")


def visible_widgets(root):
    return [w for w in [root, *root.findChildren(QWidget)] if w.isVisible()]


def audit(themes, sizes, pages, out: Path | None, deep: bool = False) -> dict:
    app = QApplication.instance() or QApplication([])
    found: dict[tuple, str] = {}
    for theme in themes:
        ThemeManager.set_theme(theme)
        for width, height in sizes:
            window = StudioWindow()
            window.resize(width, height)
            window.show()
            for name in pages:
                window.navigate(name)
                if hasattr(window.stack.currentWidget(), "ensure_built"):
                    window.stack.currentWidget().ensure_built()
                for _ in range(6):
                    app.processEvents()
                image = window.grab().toImage()
                ratio = image.devicePixelRatio()

                def report(kind, widget, detail, name=name, size=(width, height), theme=theme):
                    found.setdefault((kind, name, describe(widget), detail.split(" needs")[0][:50]), f"{theme} {size[0]}x{size[1]}: {detail}")

                page = window.stack.currentWidget()
                if deep and hasattr(page, "sections"):
                    for section in page.sections.values():
                        tabs = section.findChildren(QTabWidget, options=Qt.FindChildOption.FindDirectChildrenOnly)[-1]
                        for index in range(1, tabs.count()):
                            tabs.setCurrentIndex(index)
                            for _ in range(5):  # Layout changes settle over several passes.
                                app.processEvents()
                            for widget in visible_widgets(tabs):
                                check_widget(widget, report)
                                check_children(widget, report)
                        tabs.setCurrentIndex(0)
                    for _ in range(8):
                        app.processEvents()
                for widget in [*visible_widgets(window.sidebar), *visible_widgets(page), *visible_widgets(window.centralWidget().layout().itemAt(1).layout().itemAt(0).widget())]:
                    check_widget(widget, report)
                    check_children(widget, report)
                    check_contrast(widget, image, ratio, report)
                if out:
                    out.mkdir(parents=True, exist_ok=True)
                    window.grab().save(str(out / f"{name.replace(' ', '_')}-{theme}-{width}.png"))
            window.close()
            window.deleteLater()
            app.processEvents()
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Also save a screenshot of each page here.")
    parser.add_argument("--deep", action="store_true", help="Also open every documentation tab.")
    parser.add_argument("--themes", nargs="*", default=["light", "dark", "high-contrast"])
    args = parser.parse_args()
    found = audit(args.themes, SIZES, PAGES, args.out, args.deep)
    for key, detail in sorted(found.items()):
        print(f"{key[0]:<16} {key[1]:<20} {key[2]:<44} {detail}")
    print(f"\n{len(found)} defect(s)")
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
