# VideoPlayer

You are working with the Fluent Blue design system for PyQt6 and PySide6. Use this brief as the source of truth for this component's API, and do not invent parameters.

## Purpose

A video player with play and pause, seeking, volume, speed and full screen.

Group: Advanced Components. Qt base: `QFrame`, whose full API stays available.

## Import

```python
from fluent_blue import VideoPlayer
```

## Signature

```python
VideoPlayer(source=None, parent=None, autoplay=False, loop=False, muted=False, volume=0.8, show_controls=True, accessible_name='Video player')
```

## Parameters

| Name | Default | Description |
| --- | --- | --- |
| `source` | `None` | A file path or URL to load. |
| `parent` | `None` | Parent widget. |
| `autoplay` | `False` | Start playing as soon as the media is loaded. |
| `loop` | `False` | Start again at the end. |
| `muted` | `False` | Start muted. |
| `volume` | `0.8` | Initial volume from 0 to 1. |
| `show_controls` | `True` | Show the control bar. |
| `accessible_name` | `'Video player'` | Name for assistive technology. |

## Signals

- `position_changed(int)`: The playback position in milliseconds.
- `duration_changed(int)`: The media length in milliseconds.
- `state_changed(str)`: playing, paused or stopped.
- `ended()`: Playback reached the end and did not loop.
- `error_occurred(str)`: A readable description of why the media cannot play.

## Public methods

- `duration() -> int`
- `error() -> str`: The last error message, or an empty string.
- `is_available() -> bool`: Whether QtMultimedia loaded, so that media can actually play.
- `is_muted() -> bool`
- `loop() -> bool`
- `open_dialog()`: Ask for a video file with the native dialog and load it.
- `pause()`
- `play()`
- `position() -> int`
- `release()`: Pause and detach the media so that the backend lets go of the file and the audio device.
- `seek_by(milliseconds: int)`
- `seek_to(milliseconds: int)`: Move to a position in milliseconds, clamped to the media length.
- `set_loop(loop: bool)`: Start again at the end, or stop there.
- `set_muted(muted: bool)`
- `set_source(source: str | Path | QUrl)`: Load a file path or URL. A path that does not exist reports error_occurred at once.
- `set_speed(rate: float)`: Set the playback rate, for example 1.5 for one and a half times speed.
- `set_volume(volume: float)`: Set the volume from 0 to 1. Raising it above 0 unmutes.
- `source() -> QUrl | None`
- `speed_rate() -> float`
- `state() -> str`: playing, paused or stopped.
- `stop()`
- `toggle()`: Play when paused or stopped, pause when playing.
- `toggle_fullscreen()`: Toggle native full screen on the picture. Esc or a double click leaves it.
- `toggle_muted()`
- `volume() -> float`

## Verified example

This snippet is executed by the test suite on both Qt bindings.

```python
from fluent_blue import VideoPlayer

demo = VideoPlayer()  # Pass a path or URL, or press "Open video…": VideoPlayer("clip.mp4", autoplay=True)
demo.setMinimumHeight(300)
```

## Usage guidance

- Space plays and pauses, Left and Right seek five seconds, Up and Down change the volume, M mutes and F toggles full screen.
- It pauses by itself when hidden, so a closed tab never keeps playing sound.
- Check VideoPlayer.is_available() when you must support minimal Linux images, which can lack PulseAudio.

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
