# ToastCard

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

The card behind Toast, Notification and Snackbar.

Group: Uncatalogued. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import ToastCard
```

## Signature

```python
ToastCard(title='', message='', variant=None, kind='toast', duration=4000, action_text='', on_action=None, closable=True)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `title` | `''` | Bold first line. |
| `message` | `''` | Body text. |
| `variant` | `None` | info, success, warning or error; None hides the icon. |
| `kind` | `'toast'` | toast, notification or snackbar; sets the styling. |
| `duration` | `4000` | Milliseconds before dismissal; 0 keeps it open. |
| `action_text` | `''` | Action label. |
| `on_action` | `None` | Callable run when the action is used. |
| `closable` | `True` | Show a dismiss button. |

## Signals

- `closed()`: The card finished closing.
- `action_clicked()`: The action was used.

## Public methods

- `dismiss()`: Animate out, then emit closed and delete the card.

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
