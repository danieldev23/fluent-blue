"""Measure the operations people feel: startup, page opening, theme switching and toasts."""
from __future__ import annotations

import cProfile
import os
import pstats
import sys
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

started = time.perf_counter()
from fluent_blue import ThemeManager, Toast  # noqa: E402
from fluent_blue.compatibility.qt import BINDING, QApplication, QWidget  # noqa: E402
from fluent_blue.studio.app import StudioWindow  # noqa: E402

IMPORT_MS = (time.perf_counter() - started) * 1000
PAGES = ("Foundations", "Colors", "Typography", "Icons", "Buttons", "Inputs", "Selection", "Navigation", "Data Display", "Feedback",
         "Data Tables", "Layout", "Advanced Components", "Themes", "Playground", "About", "Changelog")


def timed(app, action, settle: int = 3) -> float:
    start = time.perf_counter()
    action()
    for _ in range(settle):
        app.processEvents()
    return (time.perf_counter() - start) * 1000


def main() -> int:
    profile_target = sys.argv[1] if len(sys.argv) > 1 else None
    app = QApplication([])
    print(f"{BINDING}  import: {IMPORT_MS:.0f} ms")
    ThemeManager.set_theme("light")
    holder = {}
    print(f"window + Overview: {timed(app, lambda: holder.setdefault('w', StudioWindow()) and holder['w'].show()):.0f} ms")
    window = holder["w"]
    window.resize(1536, 1024)
    results = {}
    results["theme, Overview only (x2 avg)"] = (timed(app, lambda: ThemeManager.set_theme("dark")) + timed(app, lambda: ThemeManager.set_theme("light"))) / 2
    results["toast, Overview only"] = timed(app, lambda: Toast.show("Saved", parent=window, variant="success", duration=500), 1)
    for name in PAGES:
        first = timed(app, lambda n=name: window.navigate(n))
        page = window.stack.currentWidget()
        complete = timed(app, page.ensure_built) if hasattr(page, "ensure_built") else 0
        print(f"open {name:<22}{first:7.0f} ms   fully built after {first + complete:5.0f} ms")
    window.navigate("Overview")
    app.processEvents()
    print(f"widgets alive: {len(window.findChildren(QWidget))}")
    results["theme, all pages built (x2 avg)"] = (timed(app, lambda: ThemeManager.set_theme("dark")) + timed(app, lambda: ThemeManager.set_theme("light"))) / 2
    results["toast, all pages built"] = timed(app, lambda: Toast.show("Saved", parent=window, variant="success", duration=500), 1)
    results["revisit Buttons"] = timed(app, lambda: window.navigate("Buttons"))
    for name, value in results.items():
        print(f"{name:<34}{value:7.0f} ms")
    if profile_target:
        action = {"theme": lambda: ThemeManager.toggle(), "toast": lambda: Toast.show("Saved", parent=window, duration=500)}[profile_target]
        profiler = cProfile.Profile()
        profiler.enable()
        action()
        for _ in range(3):
            app.processEvents()
        profiler.disable()
        pstats.Stats(profiler).sort_stats("tottime").print_stats(16)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
