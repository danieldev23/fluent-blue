"""Examples build headlessly, and the files people read stay in step with the code."""
import importlib.util
import re
from pathlib import Path

import pytest

import fluent_blue
from fluent_blue.studio import catalog

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*.py"))


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.stem)
def test_example_builds(qtbot, path):
    spec = importlib.util.spec_from_file_location(f"example_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    widget = module.build()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    assert widget.isVisible()


def test_readme_tutorial_snippets_are_valid_python():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.S)
    assert len(blocks) >= 6
    for block in blocks:
        compile(block, "<README>", "exec")


def test_readme_component_table_lists_every_catalog_entry():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    missing = [entry.name for entry in catalog.entries() if f"`{entry.name}`" not in text]
    assert missing == []


def test_changelog_copies_match():
    root = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    bundled = (ROOT / "fluent_blue" / "studio" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert root == bundled
    assert fluent_blue.__version__ in root


def test_component_docs_are_current():
    """Fails if the catalog or docstrings changed without running: python scripts/generate_docs.py --markdown-only"""
    spec = importlib.util.spec_from_file_location("generate_docs", ROOT / "scripts" / "generate_docs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert (ROOT / "docs" / "components" / "index.md").read_text(encoding="utf-8") == module.render_index()
    for group in catalog.GROUPS:
        path = ROOT / "docs" / "components" / f"{module.slug(group)}.md"
        assert path.read_text(encoding="utf-8") == module.render_group(group), group


def test_every_component_has_a_docs_screenshot():
    missing = [e.name for e in catalog.entries() if not (ROOT / "docs" / "assets" / "components" / f"{e.name}.png").exists()]
    assert missing == []
