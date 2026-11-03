"""Ready-to-use briefs that let an AI coding agent work with each Fluent Blue component.

Every brief is generated from the installed source: constructor signatures, docstrings,
signals, public methods and the catalog snippet that the test suite executes. It therefore
cannot describe an API that does not exist.

    python -m fluent_blue.agent_prompts Button          # print one brief
    python -m fluent_blue.agent_prompts --list          # list component names
    python -m fluent_blue.agent_prompts --export DIR    # write AGENTS.md, llms.txt and one file each
"""
from __future__ import annotations

import argparse
import inspect
from pathlib import Path

from .studio import catalog, introspect

PROJECT_RULES = """\
- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Never connect a lambda or closure that captures a widget to `ThemeManager` signals: it outlives the widget, and PyQt aborts when it fires. Use `ThemedMixin` or a bound method.
- Keep theme switches fast: do not rebuild child widgets in `refresh_theme()`, and free one-shot menus and dialogs with `WA_DeleteOnClose` or `finished.connect(dialog.deleteLater)`.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run."""


_INTERNAL_METHODS = {"bind_theme", "refresh_theme", "paint_gutter", "show"}


def public_classes() -> list[str]:
    """Names of every exported widget and helper class that needs a brief."""
    import fluent_blue

    skip = {"Configuration", "DesignTokens", "Theme"}
    names = []
    for name in fluent_blue.__all__:
        value = getattr(fluent_blue, name)
        if inspect.isclass(value) and name not in skip and value.__module__.startswith("fluent_blue.components"):
            names.append(name)
    return sorted(set(names))


def _entries() -> dict[str, catalog.Entry]:
    return {entry.name: entry for entry in catalog.entries()}


def _signature(cls) -> str:
    target = introspect._api_target(cls)
    label = f"{cls.__name__}.show" if target is not cls.__init__ else cls.__name__
    parameters = []
    for prop in introspect.properties(cls):
        parameters.append(prop.name if prop.default == "required" else f"{prop.name}={prop.default}")
    return f"{label}({', '.join(parameters)})"


def _methods(cls) -> list[tuple[str, str]]:
    found = {}
    for klass in cls.__mro__:
        if not klass.__module__.startswith("fluent_blue"):
            continue
        for name, value in vars(klass).items():
            if name.startswith("_") or name[0].isupper() or name in found or name in _INTERNAL_METHODS:
                continue
            function = value.__func__ if isinstance(value, (staticmethod, classmethod)) else value
            if inspect.isfunction(function) and name[0].islower() and not any(c.isupper() for c in name):
                doc = inspect.cleandoc(function.__doc__ or "").split("\n")[0]
                signature = str(inspect.signature(function)).replace("(self, ", "(").replace("(self)", "()").replace("'", "")
                found[name] = (f"{name}{signature}".replace(" -> None", ""), introspect.clean_markup(doc))
    return sorted(found.values())


def group_of(name: str) -> str:
    entry = _entries().get(name)
    return entry.group if entry else "Uncatalogued"


def component_prompt(name: str) -> str:
    """Return the Markdown brief for one component. Raises ``KeyError`` for an unknown name."""
    if name not in public_classes():
        raise KeyError(f"Unknown component {name!r}. Available: {', '.join(public_classes())}")
    import fluent_blue

    cls = getattr(fluent_blue, name)
    entry = _entries().get(name)
    bases = [b.__name__ for b in cls.__mro__[1:] if b.__module__.split(".")[0] in ("PyQt6", "PySide6")]
    lines = [
        f"# {name}", "",
        "You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.", "",
        "## Purpose", "", introspect.summary(cls), "",
        f"Group: {group_of(name)}. " + (f"Qt base: `{bases[0]}`, whose full API stays available." if bases else "Plain Python helper."), "",
        "## Import", "", "```python", f"from fluent_blue import {name}", "```", "",
        "## Signature", "", "```python", _signature(cls), "```", "",
    ]
    props = [p for p in introspect.properties(cls)]
    if props:
        lines += ["## Parameters", "", "| Name | Default | Description |", "| --- | --- | --- |"]
        lines += [f"| `{p.name}` | `{p.default}` | {introspect.clean_markup(p.description).replace('|', chr(92) + '|')} |" for p in props]
        lines.append("")
    signals = introspect.signals(cls)
    note = introspect.inherited_signals_note(cls)
    if signals or note:
        lines += ["## Signals", ""]
        lines += [f"- `{s.name}({s.args})`: {introspect.clean_markup(s.description)}" for s in signals]
        if note:
            lines.append(f"- {introspect.clean_markup(note)}")
        lines.append("")
    methods = _methods(cls)
    if methods:
        lines += ["## Public methods", ""]
        lines += [f"- `{signature}`" + (f": {doc}" if doc else "") for signature, doc in methods]
        lines.append("")
    if entry:
        lines += ["## Verified example", "", "This snippet is executed by the test suite on both Qt bindings.", "", "```python", entry.code.strip(), "```", ""]
        lines += ["## Usage guidance", ""] + [f"- {tip}" for tip in entry.tips] + [""]
    lines += ["## Project rules", "", PROJECT_RULES, ""]
    return "\n".join(lines)


def library_prompt() -> str:
    """Return the brief for the whole library, suitable for ``AGENTS.md``."""
    lines = [
        "# Fluent Blue: guide for AI coding agents", "",
        "Fluent Blue is a design system for Python desktop applications on PyQt6 and PySide6.", "",
        "## Rules", "", PROJECT_RULES, "",
        "## Quick start", "", "```python",
        "from fluent_blue import Button, Card, ThemeManager",
        "from fluent_blue.compatibility.qt import QApplication, QVBoxLayout", "",
        "app = QApplication([])", 'ThemeManager.set_theme("light")', "card = Card()", "layout = QVBoxLayout(card)",
        'layout.addWidget(Button("Get Started", variant="primary"))', "card.show()", "app.exec()", "```", "",
        "## Component briefs", "",
        "Read the brief for a component before you use or change it. Print one with `python -m fluent_blue.agent_prompts <Name>`.", "",
    ]
    grouped: dict[str, list[str]] = {}
    for name in public_classes():
        grouped.setdefault(group_of(name), []).append(name)
    for group in (*catalog.GROUPS, "Uncatalogued"):
        if group in grouped:
            lines += [f"### {group}", ""]
            import fluent_blue

            for name in grouped[group]:
                lines.append(f"- [`{name}`](docs/ai/components/{name}.md): {introspect.summary(getattr(fluent_blue, name))}")
            lines.append("")
    return "\n".join(lines)


def llms_txt() -> str:
    """Return an index in the llms.txt format."""
    import fluent_blue

    lines = ["# Fluent Blue", "", "> A design system for Python desktop applications on PyQt6 and PySide6.", "", "## Components", ""]
    lines += [f"- [{n}](docs/ai/components/{n}.md): {introspect.summary(getattr(fluent_blue, n))}" for n in public_classes()]
    return "\n".join(lines) + "\n"


def export(root: Path) -> int:
    """Write ``AGENTS.md``, ``llms.txt`` and ``docs/ai/components/*.md``. Returns the brief count."""
    folder = root / "docs" / "ai" / "components"
    folder.mkdir(parents=True, exist_ok=True)
    names = public_classes()
    for stale in folder.glob("*.md"):
        if stale.stem not in names:
            stale.unlink()
    for name in names:
        (folder / f"{name}.md").write_text(component_prompt(name), encoding="utf-8")
    (root / "AGENTS.md").write_text(library_prompt(), encoding="utf-8")
    (root / "llms.txt").write_text(llms_txt(), encoding="utf-8")
    return len(names)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print or export Fluent Blue briefs for AI coding agents.")
    parser.add_argument("component", nargs="?", help="Component name, such as Button.")
    parser.add_argument("--list", action="store_true", help="List component names.")
    parser.add_argument("--library", action="store_true", help="Print the whole-library brief.")
    parser.add_argument("--export", type=Path, metavar="DIR", help="Write AGENTS.md, llms.txt and docs/ai/components/ under DIR.")
    args = parser.parse_args(argv)
    if args.export:
        print(f"Wrote {export(args.export)} component briefs to {args.export}")
    elif args.list:
        print("\n".join(public_classes()))
    elif args.library:
        print(library_prompt())
    elif args.component:
        print(component_prompt(args.component))
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
