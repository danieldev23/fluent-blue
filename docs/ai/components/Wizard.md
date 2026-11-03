# Wizard

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A multi-step flow with a stepper, validation and navigation.

Group: Advanced Components. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import Wizard
```

## Signature

```python
Wizard(parent=None, finish_text='Finish', cancelable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `parent` | `None` | Parent widget. |
| `finish_text` | `'Finish'` | Label of the last step's button. |
| `cancelable` | `False` | Show a cancel button. |

## Signals

- `page_changed(int)`: The current page changed.
- `finished()`: The last page was completed.
- `cancelled()`: The cancel button was used.

## Public methods

- `add_page(title: str, widget, validator=None) -> int`: Add a step.
- `back()`: Return to the previous page.
- `current() -> int`
- `next() -> bool`: Validate and advance, finishing on the last page. Returns False if blocked.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import FormField, Input, Result, Text, Wizard

demo = Wizard()
name = Input(placeholder="Required")
field = FormField("Project name", name, helper="Next is blocked until this has a value.")

def check():
    field.set_error("" if name.text() else "Enter a project name.")
    return bool(name.text())

demo.add_page("Details", field, check)
demo.add_page("Review", Text("Check your details, then continue.", color="text-secondary"))
demo.add_page("Finish", Result("success", "All set", description="Your project is ready."))
demo.setMinimumHeight(330)
```

## Usage guidance

- Validate on Next so that errors appear in context, on the step that caused them.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
