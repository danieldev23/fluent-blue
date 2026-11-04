"""Capture real screenshots of Design Studio for the README and the documentation.

    python scripts/capture_screenshots.py            # writes assets/screenshots/*.png
    python scripts/capture_screenshots.py --docs     # also copies them to docs/assets/screenshots

Every image is a grab of the live application at 1536x1024, rendered headlessly.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fluent_blue import Drawer, Notification, Snackbar, ThemeManager, Toast  # noqa: E402
from fluent_blue.compatibility.qt import QApplication, QThread  # noqa: E402
from fluent_blue.studio.app import StudioWindow  # noqa: E402

OUT = ROOT / "assets" / "screenshots"
PAGES = ("Overview", "Foundations", "Colors", "Typography", "Icons", "Buttons", "Inputs", "Selection", "Navigation", "Data Display",
         "Data Tables", "Feedback", "Layout", "Advanced Components", "Themes", "Playground")
DARK_PAGES = ("Overview", "Colors", "Buttons", "Data Tables", "Advanced Components")
SIZE = (1536, 1024)


def slug(name: str) -> str:
    return name.lower().replace(" ", "-")


def pump(app, frames: int = 12, delay_ms: int = 8) -> None:
    for _ in range(frames):
        app.processEvents()
        QThread.msleep(delay_ms)


def capture(theme: str, pages, app) -> list[Path]:
    ThemeManager.set_theme(theme)
    window = StudioWindow()
    window.resize(*SIZE)
    window.show()
    pump(app)
    written = []
    for name in pages:
        window.navigate(name)
        page = window.stack.currentWidget()
        if hasattr(page, "ensure_built"):
            page.ensure_built()
        pump(app, 16)
        path = OUT / f"{slug(name)}-{theme}.png"
        window.grab().save(str(path))
        written.append(path)
    if theme == "light":
        window.navigate("Overview")
        pump(app)
        Toast.show("Saved successfully", parent=window, variant="success", duration=0)
        Toast.show("Disk usage is above 90%", parent=window, variant="warning", duration=0)
        Notification.show("Export finished", "Your report is ready to download.", parent=window, variant="success", action_text="Open")
        Snackbar.show("Item archived", parent=window, action_text="Undo", duration=0)
        pump(app, 30)
        path = OUT / "feedback-overlays-light.png"
        window.grab().save(str(path))
        written.append(path)
        drawer = Drawer(window, title="Edit profile")
        from fluent_blue import Button, FormField, Input

        drawer.add(FormField("Name", Input("Ada Lovelace")))
        drawer.add(Button("Save", variant="primary"))
        drawer.body.addStretch(1)
        drawer.open_drawer()
        pump(app, 40)
        path = OUT / "drawer-light.png"
        window.grab().save(str(path))
        written.append(path)
    window.close()
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs", action="store_true", help="Also copy the images to docs/assets/screenshots.")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication([])
    written = capture("light", PAGES, app) + capture("dark", DARK_PAGES, app)
    if args.docs:
        target = ROOT / "docs" / "assets" / "screenshots"
        target.mkdir(parents=True, exist_ok=True)
        for path in written:
            shutil.copy(path, target / path.name)
    total = sum(p.stat().st_size for p in written) / 1e6
    print(f"Wrote {len(written)} screenshots ({total:.1f} MB) to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
