# Troubleshooting

## `BindingError: Fluent Blue needs a Qt binding`

Neither PyQt6 nor PySide6 is installed in the active environment. Install one extra: `pip install "fluent-blue[pyqt6]"`.

## `BindingError: PyQt6 and PySide6 are both loaded`

Something imported the other binding before Fluent Blue. Remove one binding from the environment, or set `FLUENT_BLUE_QT_BINDING` to the one you want and make sure nothing imports the other.

## `Fatal Python error: bool_dealloc` or an abort on exit with PySide6

You are running PySide6 on Linux with Python 3.11. The Linux wheels of PySide6 6.9 to 6.12 corrupt the reference count of `True`/`False` when custom signals are emitted; Python 3.12 and later tolerate it. Upgrade Python to 3.12 or newer, or use PyQt6.

## `VideoPlayer` says "Video playback is unavailable"

Qt could not load QtMultimedia. On minimal Linux images install PulseAudio's client library and, for common formats, the FFmpeg runtime: `sudo apt-get install -y libpulse0 libpulse-mainloop-glib0 ffmpeg`. Check `VideoPlayer.is_available()` at start-up if your application must work without it.

## `VideoPlayer` shows "This file could not be played"

The format or codec is not supported by Qt's media backend on this system. MP4 with H.264 and AAC plays everywhere; convert other files with `ffmpeg -i input.mkv -pix_fmt yuv420p output.mp4`.

## Nothing shows, or the process exits at once

A `QApplication` must exist before any widget, and `app.exec()` must run. The examples in `examples/` show the shape.

## Qt platform plugin errors on Linux

`qt.qpa.plugin: Could not load the Qt platform plugin "xcb"` means system libraries are missing. Install `libegl1 libgl1 libopengl0 libxkbcommon-x11-0 libxcb-cursor0 libdbus-1-3 libfontconfig1`, or set `QT_QPA_PLATFORM=offscreen` for headless use.

## Fonts look different from the screenshots

Fluent Blue prefers Segoe UI, then the platform's system font, then Inter, Noto Sans, Ubuntu and Cantarell. Install one of them, or override `font_families` in a custom theme's `tokens`.

## Widgets painted with the wrong colors after a theme switch

The widget caches a color or pixmap. Subclass `ThemedMixin`, call `bind_theme()` and rebuild the cache in `refresh_theme()`. See [Theming](theming.md).

## `RuntimeError: wrapped C/C++ object has been deleted` during a theme switch

A lambda that captured a widget was connected to `ThemeManager.theme_changed`. Replace it with `ThemedMixin` or a bound method, which Qt disconnects when the widget is destroyed.

## A dialog's buttons do nothing

Dialogs created in a local function are garbage-collected when the function returns if nothing holds them. Give the dialog a parent, keep a reference, or use `dialog.open()` and connect `finished` to `deleteLater`.

## Toasts never appear

`Toast.show` needs a parent in the target window, or an active window. Pass any widget of that window as `parent`.

## The UI audit reports a defect in my page

`scripts/ui_audit.py` reports clipped text, widgets squeezed below their minimum size, overlapping siblings and low contrast, with the widget path, theme and window size. Most fixes are a minimum width, a word-wrap setting or a token change. Run it with `--deep` to include the documentation tabs.

## Tests hang on Windows

Set `QT_QPA_PLATFORM=offscreen` and run `pytest -p no:cacheprovider`. Native file dialogs block without a person; the suite stubs them, so do the same in your tests.
