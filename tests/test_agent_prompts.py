"""Every public component must have an accurate brief for AI coding agents."""
import inspect
import re

import pytest

import fluent_blue
from fluent_blue import agent_prompts
from fluent_blue.studio import catalog, introspect

NAMES = agent_prompts.public_classes()


def test_every_public_component_has_a_catalog_entry():
    known = {entry.name for entry in catalog.entries()}
    helpers = {"Command", "DataTableModel", "DrawerScrim", "FieldLabel", "FieldMessage", "FloatingTooltip", "ModalScrim",
               "RichTextArea", "SyntaxHighlighter", "TimePopup", "ToastCard"}
    assert sorted(set(NAMES) - known - helpers) == []


@pytest.mark.parametrize("name", NAMES)
def test_brief_has_required_sections(name):
    brief = agent_prompts.component_prompt(name)
    for section in (f"# {name}", "## Purpose", "## Import", "## Signature", "## Project rules"):
        assert section in brief
    assert ":class:" not in brief and "``" not in brief.replace("```", "")


@pytest.mark.parametrize("name", NAMES)
def test_brief_lists_every_constructor_parameter(name):
    cls = getattr(fluent_blue, name)
    brief = agent_prompts.component_prompt(name)
    target = introspect._api_target(cls)
    for parameter in inspect.signature(target).parameters.values():
        if parameter.name != "self" and parameter.kind not in (parameter.VAR_KEYWORD, parameter.VAR_POSITIONAL):
            assert f"`{parameter.name}`" in brief


@pytest.mark.parametrize("name", NAMES)
def test_every_parameter_is_described(name):
    missing = [p.name for p in introspect.properties(getattr(fluent_blue, name)) if not p.description]
    assert missing == [], f"{name} has undocumented parameters"


@pytest.mark.parametrize("name", NAMES)
def test_brief_lists_every_declared_signal(name):
    brief = agent_prompts.component_prompt(name)
    for signal in introspect.signals(getattr(fluent_blue, name)):
        assert f"`{signal.name}(" in brief


@pytest.mark.parametrize("entry", catalog.entries(), ids=lambda e: e.name)
def test_brief_example_runs(qtbot, entry):
    brief = agent_prompts.component_prompt(entry.name)
    code = re.search(r"## Verified example.*?```python\n(.*?)```", brief, re.S).group(1)
    scope = {}
    exec(code, scope)
    qtbot.addWidget(scope["demo"])
    assert scope["demo"] is not None


def test_unknown_name_is_rejected():
    with pytest.raises(KeyError):
        agent_prompts.component_prompt("NotAComponent")


def test_export_writes_all_files(tmp_path):
    assert agent_prompts.export(tmp_path) == len(NAMES)
    assert (tmp_path / "AGENTS.md").read_text().count("docs/ai/components/") == len(NAMES)
    assert (tmp_path / "llms.txt").exists()
    assert len(list((tmp_path / "docs/ai/components").glob("*.md"))) == len(NAMES)


def test_committed_briefs_are_current():
    """Fails if the API changed without running: python -m fluent_blue.agent_prompts --export ."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for name in NAMES:
        assert (root / "docs/ai/components" / f"{name}.md").read_text(encoding="utf-8") == agent_prompts.component_prompt(name), name
    assert (root / "AGENTS.md").read_text(encoding="utf-8") == agent_prompts.library_prompt()
