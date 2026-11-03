# Contributing to Fluent Blue

Thank you for helping. This guide explains how the project is organised, what a change needs before it is merged, and how to add a component.

## Set up

```bash
git clone https://github.com/danieldev23/fluent-blue
cd fluent-blue
python -m venv .venv-pyqt && .venv-pyqt/bin/pip install -e ".[dev,pyqt6]"
python -m venv .venv-pyside && .venv-pyside/bin/pip install -e ".[dev,pyside6]"
```

Two environments, because the library must work on both bindings and they cannot share a process.

## Before you open a pull request

Run all of these. CI runs them too, but it is faster to find problems locally.

```bash
ruff check .
.venv-pyqt/bin/pytest
.venv-pyside/bin/pytest
QT_QPA_PLATFORM=offscreen .venv-pyqt/bin/python scripts/ui_audit.py --deep
.venv-pyqt/bin/python -m fluent_blue.agent_prompts --export .
.venv-pyqt/bin/python scripts/generate_docs.py --markdown-only
```

The last two regenerate files that tests compare against the source. Commit their output.

Do not report a result you did not run. If something cannot be verified on your machine, say so in the pull request.

## Rules of the code base

- Import Qt from `fluent_blue.compatibility.qt`, never from `PyQt6` or `PySide6` directly.
- Components read design tokens; they never hardcode colors, spacing, radii or fonts, and never call `setStyleSheet`.
- Styling lives in `fluent_blue/themes/stylesheet/`, keyed by class name and dynamic properties such as `variant`.
- Custom-painted widgets read `ThemeManager` colors inside `paintEvent`. Cached assets are rebuilt in `refresh_theme()` of a `ThemedMixin` subclass.
- Never connect a lambda that captures a widget to a `ThemeManager` signal. The connection outlives the widget and aborts the process when it fires.
- Fluent Blue methods and signals are `snake_case`; inherited Qt API stays `camelCase`.
- Text must reach 4.5:1 contrast in every built-in theme. `tests/test_contrast.py` checks the token pairs; the UI audit checks rendered pixels.
- One-shot menus and dialogs free themselves (`WA_DeleteOnClose`, or `finished.connect(dialog.deleteLater)`), so long sessions do not slow down.

## Adding a component

1. Implement it in the matching `fluent_blue/components/<group>/` module with a docstring that has `Args:` and `Signals:` sections. The documentation, Design Studio and AI briefs are generated from these.
2. Export it from the group's `__init__.py`.
3. Add stylesheet rules to `fluent_blue/themes/stylesheet/<group>.py`.
4. Add a catalog entry in `fluent_blue/studio/catalog/<group>.py`: a runnable snippet that assigns a widget to `demo`, plus one or two usage tips. The snippet is executed by the tests on both bindings and in every theme, shown live in Design Studio, printed in the docs and embedded in the AI brief.
5. Write tests for behaviour and signals in `tests/`.
6. Run the checks above and regenerate briefs and docs.

## Commit messages

Use the imperative mood and explain why, not just what. Reference issues where they exist.

## Reporting bugs

Open an issue with the binding and versions (`python -c "import fluent_blue as f; print(f.BINDING, f.BINDING_VERSION, f.QT_VERSION)"`), the operating system, a minimal snippet, and what you expected. A screenshot helps for visual problems.
