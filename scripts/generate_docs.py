"""Generate the component documentation and its screenshots from the catalog.

    python scripts/generate_docs.py                  # Markdown and screenshots
    python scripts/generate_docs.py --markdown-only  # Markdown only; CI compares it with the repo

The Markdown is deterministic and is checked by ``tests/test_docs_current.py``. Screenshots are
rendered headlessly in the light theme and depend on the platform's fonts, so they are
regenerated on demand rather than compared.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import fluent_blue  # noqa: E402
from fluent_blue.studio import catalog, introspect  # noqa: E402
from fluent_blue.studio.pages.components import _DESCRIPTIONS  # noqa: E402

DOCS = ROOT / "docs"
SHOTS = DOCS / "assets" / "components"


def slug(group: str) -> str:
    return group.lower().replace(" ", "-")


def _escape(text: str) -> str:
    return introspect.clean_markup(text).replace("|", "\\|")


def render_entry(entry: catalog.Entry) -> str:
    cls = entry.cls
    lines = [f"## {entry.name}", "", introspect.summary(cls), "",
             f"![{entry.name}](../assets/components/{entry.name}.png)", "",
             "```python", entry.code.strip(), "```", ""]
    props = introspect.properties(cls)
    if props:
        lines += ["**Properties**", "", "| Name | Default | Description |", "| --- | --- | --- |"]
        lines += [f"| `{p.name}` | `{p.default}` | {_escape(p.description)} |" for p in props]
        lines.append("")
    signals = introspect.signals(cls)
    note = introspect.inherited_signals_note(cls)
    if signals or note:
        lines += ["**Signals**", ""]
        lines += [f"- `{s.name}({s.args})`: {introspect.clean_markup(s.description)}" for s in signals]
        if note:
            lines.append(f"- {introspect.clean_markup(note)}")
        lines.append("")
    if entry.tips:
        lines += ["**Best practices**", ""] + [f"- {tip}" for tip in entry.tips] + [""]
    lines += [f"[AI brief for {entry.name}](../ai/components/{entry.name}.md){{ .md-button }}", ""]
    return "\n".join(lines)


def render_group(group: str) -> str:
    lines = [f"# {group}", "", _DESCRIPTIONS.get(group, ""), "",
             "Every example below is executed by the test suite on PyQt6 and PySide6, in each built-in theme.", ""]
    for entry in catalog.by_group(group):
        lines.append(render_entry(entry))
    return "\n".join(lines).rstrip() + "\n"


def render_index() -> str:
    lines = ["# Components", "", "Fluent Blue has one page per group. Each component shows a live-rendered screenshot, the verified "
             "example, its properties and signals, and a link to its brief for AI coding agents.", "",
             "| Group | Components |", "| --- | --- |"]
    for group in catalog.GROUPS:
        names = ", ".join(f"[`{e.name}`]({slug(group)}.md#{e.name.lower()})" for e in catalog.by_group(group))
        lines.append(f"| [{group}]({slug(group)}.md) | {names} |")
    return "\n".join(lines) + "\n"


def write_markdown() -> list[Path]:
    folder = DOCS / "components"
    folder.mkdir(parents=True, exist_ok=True)
    written = [folder / "index.md"]
    written[0].write_text(render_index(), encoding="utf-8")
    for group in catalog.GROUPS:
        path = folder / f"{slug(group)}.md"
        path.write_text(render_group(group), encoding="utf-8")
        written.append(path)
    return written


def write_screenshots() -> int:
    from fluent_blue import ThemeManager
    from fluent_blue.compatibility.qt import QApplication, QVBoxLayout, QWidget

    app = QApplication.instance() or QApplication([])
    ThemeManager.set_theme("light")
    SHOTS.mkdir(parents=True, exist_ok=True)
    count = 0
    for entry in catalog.entries():
        frame = QWidget()
        frame.setObjectName("docsFrame")
        frame.setStyleSheet(f"#docsFrame {{ background: {ThemeManager.color('surface')}; }}")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(entry.run())
        frame.setFixedWidth(760)
        frame.adjustSize()
        frame.show()
        for _ in range(6):
            app.processEvents()
        frame.grab().save(str(SHOTS / f"{entry.name}.png"))
        frame.close()
        frame.deleteLater()
        app.processEvents()
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown-only", action="store_true")
    args = parser.parse_args()
    written = write_markdown()
    print(f"Wrote {len(written)} Markdown files for {len(catalog.entries())} components ({fluent_blue.BINDING}).")
    if not args.markdown_only:
        print(f"Rendered {write_screenshots()} screenshots into {SHOTS.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
