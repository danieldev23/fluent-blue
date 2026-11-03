# FormField

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

Label, control, helper text and error message as one unit.

Group: Inputs. Qt base: `QWidget`, whose full API stays available.

## Import

```python
from fluent_blue import FormField
```

## Signature

```python
FormField(label='', control=None, parent=None, helper='', required=False, validator=None)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `label` | `''` | Field label, linked to the control as its buddy for keyboard access. |
| `control` | `None` | The input widget. |
| `parent` | `None` | Parent widget. |
| `helper` | `''` | Helper text shown when there is no error. |
| `required` | `False` | Append a required marker to the label. |
| `validator` | `None` | Optional callable(value) -> str \| None returning an error message. It runs on validate() and when an input finishes editing. |

## Signals

- `validated(bool)`: Emitted after validation with the outcome.

## Public methods

- `error() -> str`
- `set_error(message: str = )`: Show an error, or clear it with an empty message.
- `set_helper(helper: str)`
- `validate() -> bool`: Run the validator and show its result. Returns True when the value is valid.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import FormField, Input, Stack

def check_email(value):
    return None if "@" in value else "Enter a valid email address."

email = FormField("Work email", Input(placeholder="name@company.com"), required=True,
                  helper="Used for sign-in only.", validator=check_email)
email.validate()
name = FormField("Display name", Input("Ada Lovelace"), helper="Shown to your team.")
demo = Stack([email, name], spacing=4)
```

## Usage guidance

- Validate when the field loses focus, not on each keystroke.
- Say how to fix the problem, not just that one exists.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Never connect a lambda or closure that captures a widget to `ThemeManager` signals: it outlives the widget, and PyQt aborts when it fires. Use `ThemedMixin` or a bound method.
- Keep theme switches fast: do not rebuild child widgets in `refresh_theme()`, and free one-shot menus and dialogs with `WA_DeleteOnClose` or `finished.connect(dialog.deleteLater)`.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
