# StatisticCard

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A headline metric with trend.

Group: Data Display. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import StatisticCard
```

## Signature

```python
StatisticCard(title='', value='', parent=None, delta='', trend='flat', caption='', icon=None, spark=None, positive_is_up=True, subtitle='', elevation=0, tone='default', hoverable=False, clickable=False)
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `title` | `''` | Metric name. |
| `value` | `''` | Formatted value. |
| `parent` | `None` | Parent widget. |
| `delta` | `''` | Change text, such as "+12.4%". |
| `trend` | `'flat'` | up, down or flat. It sets the delta color. |
| `caption` | `''` | Text after the delta, such as "vs last week". |
| `icon` | `None` | Icon name. |
| `spark` | `None` | Optional numbers for a sparkline. |
| `positive_is_up` | `True` | Set False when a falling number is good, such as error rate. |
| `subtitle` | `''` | Header subtitle. |
| `elevation` | `0` | Shadow level from 0 to 4. |
| `tone` | `'default'` | default, secondary or brand. |
| `hoverable` | `False` | Highlight the border on hover. |
| `clickable` | `False` | Make the card activatable by mouse and keyboard. |

## Signals

- `clicked()`: A clickable card was activated.

## Public methods

- `add(widget, stretch: int = 0)`: Add a widget to the content layout and return it.
- `content_layout() -> QVBoxLayout`: Return the card's layout with token padding, creating it if necessary.
- `set_elevation(level: int)`
- `set_value(value: str)`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import Grid, StatisticCard

demo = Grid(columns=3)
demo.add(StatisticCard("Revenue", "$48.2k", delta="+12.4%", trend="up", caption="vs last month", icon="chart-line",
                       spark=[3, 4, 3.6, 5, 4.8, 6, 7.2]))
demo.add(StatisticCard("Active users", "2,840", delta="+3.1%", trend="up", caption="vs last week", icon="users",
                       spark=[6, 5.8, 6.2, 6, 6.4, 6.6, 6.5]))
demo.add(StatisticCard("Error rate", "0.42%", delta="-0.08%", trend="down", caption="vs yesterday", icon="alert-triangle",
                       positive_is_up=False, spark=[5, 4.6, 4.8, 3.9, 3.2, 3.4, 2.9]))
```

## Usage guidance

- Always give the number a comparison; a lone figure says little.
- Set positive_is_up=False for metrics where lower is better.

## Project rules

- Import components from `fluent_blue`, and Qt names from `fluent_blue.compatibility.qt`. Never import `PyQt6` or `PySide6` directly in library code, and never load both in one process.
- Style through props and design tokens. Do not call `setStyleSheet` on components, and do not hardcode colors, spacing, radii or fonts.
- Read theme values with `ThemeManager.color("role")`, `.qcolor("role")`, `.spacing(step)`, `.radius("md")` and `.font("role")`. For custom painting, read them inside `paintEvent`.
- Subclass with `ThemedMixin`, call `self.bind_theme()`, and rebuild cached pixmaps in `refresh_theme()`, so that runtime theme switches work.
- Use icon names from `icon_names()`, or add one with `register_icon`. Icon-only controls need a `tooltip`, which also becomes the accessible name.
- Text needs at least 4.5:1 contrast. Keep keyboard access and visible focus.
- Fluent Blue signals and methods use `snake_case`. Inherited Qt API stays `camelCase`.
- Verify your change on both bindings: `FLUENT_BLUE_QT_BINDING=PyQt6 pytest` and `FLUENT_BLUE_QT_BINDING=PySide6 pytest`, then `python scripts/ui_audit.py`. Never report a result you did not run.
