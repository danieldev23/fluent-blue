"""The component catalog: a single source for Design Studio pages, documentation and tests.

Each entry's ``code`` is a runnable snippet that assigns a widget to ``demo``. Studio runs
it for the live preview, the docs print it, and the test suite executes it on both Qt
bindings in every theme, so published examples cannot go stale.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Entry:
    name: str
    group: str
    code: str
    tips: list[str] = field(default_factory=list)
    summary: str = ""

    @property
    def cls(self):
        import fluent_blue

        return getattr(fluent_blue, self.name)

    def run(self):
        """Execute the snippet and return the ``demo`` widget."""
        scope: dict = {}
        exec(compile(self.code, f"<catalog {self.name}>", "exec"), scope)  # noqa: S102 - trusted, in-package source
        return scope["demo"]


GROUPS = ("Buttons", "Inputs", "Selection", "Navigation", "Data Display", "Data Tables", "Feedback", "Layout", "Advanced Components")


def entries() -> list[Entry]:
    from . import added, advanced, buttons, data_tables, display, feedback, inputs, layout, navigation, selection

    result: list[Entry] = []
    for module in (buttons, inputs, selection, navigation, display, data_tables, feedback, layout, advanced, added):
        result += module.ENTRIES
    return result


def by_group(group: str) -> list[Entry]:
    return [e for e in entries() if e.group == group]
