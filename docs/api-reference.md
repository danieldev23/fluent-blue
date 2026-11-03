# API reference

The reference is generated from the source: constructor signatures, `Args:` and `Signals:` docstring sections, declared signals and public methods. Three views of the same data exist, and tests fail if any of them falls behind the code.

| Where | What |
| --- | --- |
| [Component pages](components/index.md) | Screenshot, verified example, properties, signals and best practices per component. |
| Design Studio | The Properties and Signals tabs of every component, plus a live event readout under each preview. |
| [AI briefs](ai-agents.md) | One Markdown brief per component for coding assistants, with public methods. |

## Package layout

| Module | Contents |
| --- | --- |
| `fluent_blue` | Every component, `ThemeManager`, `configure`, `config`, icon helpers, `BINDING`, `BINDING_VERSION`, `QT_VERSION`, `__version__`. |
| `fluent_blue.compatibility.qt` | Re-exports of the active binding's `QtCore`, `QtGui`, `QtWidgets` and `QtSvg` names, plus `Signal`, `Slot`, `Property` and `delete_now`. |
| `fluent_blue.core` | `ThemeManager`, `Theme`, `DesignTokens`, `TypeStyle`, `Shadow`, `Configuration`. |
| `fluent_blue.core.palette` | Pure color math: `parse_hex`, `mix`, `with_alpha`, `contrast_ratio`, `readable_on`, `derive_ramp`, the built-in theme palettes. |
| `fluent_blue.core.animations` | `animate`, `fade`, `apply_elevation`. |
| `fluent_blue.icons` | `icon`, `icon_pixmap`, `icon_svg`, `icon_names`, `has_icon`, `register_icon`, `register_icon_file`. |
| `fluent_blue.components.base` | `ThemedMixin`, `set_style_prop`, `repolish`, `check_choice`, `normalize_options`. |
| `fluent_blue.studio` | Design Studio: `app.StudioWindow`, `app.main`, the `catalog` and `introspect`. |
| `fluent_blue.agent_prompts` | `component_prompt`, `library_prompt`, `export`, `public_classes`. |

## Conventions

- Fluent Blue methods and signals are `snake_case`; inherited Qt API is `camelCase`.
- Choice arguments are validated: an unsupported `variant`, `size` or `placement` raises `ValueError` with the allowed values.
- Options for `Select`, `ComboBox`, `MultiSelect`, `RadioGroup` and `SegmentedControl` accept `"text"`, `("Label", value)` or `{"label": ..., "value": ...}`.
- Signals that report a value carry the Python value (`value_changed(object)`), not a Qt index.
- Dates and times use `datetime.date` and `datetime.time`.

## Generating the reference

```bash
python scripts/generate_docs.py                 # component pages and screenshots
python -m fluent_blue.agent_prompts --export .  # AI briefs, AGENTS.md and llms.txt
```
