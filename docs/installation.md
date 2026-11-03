# Installation

## Requirements

- Python 3.11 or 3.13 (tested). Python 3.12 should work but is not part of the test matrix yet.
- One Qt binding: PyQt6 or PySide6, version 6.5 or later. Verified with 6.12.

Fluent Blue has no other dependencies.

## Install

Choose one binding. The library never loads both in one process, and the extras keep an install from pulling in both by accident.

=== "PyQt6"

    ```bash
    pip install "fluent-blue[pyqt6]"
    ```

=== "PySide6"

    ```bash
    pip install "fluent-blue[pyside6]"
    ```

If a binding is already installed, `pip install fluent-blue` is enough. Fluent Blue picks the binding that is already imported, then the one named in `FLUENT_BLUE_QT_BINDING`, then whichever of PyQt6 and PySide6 it finds first.

## Open Design Studio

```bash
fluent-blue-studio
```

The showcase opens on the Overview board. Press ++ctrl+k++ to search components.

## Check the installation

```python
import fluent_blue
print(fluent_blue.__version__, fluent_blue.BINDING, fluent_blue.BINDING_VERSION, "Qt", fluent_blue.QT_VERSION)
```

## Linux notes

Qt needs a few system libraries that minimal images lack. On Debian and Ubuntu:

```bash
sudo apt-get install -y libegl1 libgl1 libopengl0 libxkbcommon-x11-0 libxcb-cursor0 libdbus-1-3 libfontconfig1
```

For headless use, such as CI, set `QT_QPA_PLATFORM=offscreen`.

## From source

```bash
git clone https://github.com/danieldev23/fluent-blue
cd fluent-blue
pip install -e ".[dev,pyqt6]"
pytest
```

See [Contributing](contributing.md) for the full development workflow.
