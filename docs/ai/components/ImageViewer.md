# ImageViewer

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

An image viewer with zoom, pan, rotate and fit.

Group: Advanced Components. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import ImageViewer
```

## Signature

```python
ImageViewer(image=None, parent=None, min_zoom=0.05, max_zoom=16.0)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `image` | `None` | Path or QPixmap. |
| `parent` | `None` | Parent widget. |
| `min_zoom` | `0.05` | Lowest zoom factor. |
| `max_zoom` | `16.0` | Highest zoom factor. |

## Signals

- `zoom_changed(float)`: The new zoom factor.

## Public methods

- `fit()`: Scale the image to fit the view.
- `has_image() -> bool`
- `rotate(degrees: int = 90)`: Rotate clockwise.
- `set_image(image) -> bool`: Load an image from a path or QPixmap. Returns False if it could not load.
- `set_zoom(zoom: float)`: Set an absolute zoom factor, clamped to the limits.
- `zoom() -> float`
- `zoom_by(factor: float)`: Multiply the current zoom.

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import ImageViewer, ThemeManager
from fluent_blue.compatibility.qt import QLinearGradient, QPainter, QPixmap

picture = QPixmap(640, 360)
painter = QPainter(picture)
gradient = QLinearGradient(0, 0, 640, 360)
gradient.setColorAt(0, ThemeManager.qcolor("primary-800"))
gradient.setColorAt(1, ThemeManager.qcolor("primary-300"))
painter.fillRect(picture.rect(), gradient)
painter.end()
demo = ImageViewer(picture)
demo.setMinimumHeight(280)
```

## Usage guidance

- The mouse wheel zooms under the cursor, and dragging pans the image.

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
