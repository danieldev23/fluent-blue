"""Single import point for the active Qt binding.

Fluent Blue supports PyQt6 and PySide6 from the same source tree. Every module in
the package imports Qt names from here, so no other module knows which binding is
active. Selection order:

1. A binding already imported by the host application.
2. The ``FLUENT_BLUE_QT_BINDING`` environment variable (``PyQt6`` or ``PySide6``).
3. PyQt6, then PySide6, whichever is installed first.

Loading both bindings in one process is unsafe, so that raises immediately.
"""
from __future__ import annotations

import importlib
import os
import sys

SUPPORTED_BINDINGS = ("PyQt6", "PySide6")


class BindingError(ImportError):
    """Raised when no usable Qt binding exists or the selection is conflicting."""


def _select_binding() -> str:
    loaded = [name for name in SUPPORTED_BINDINGS if name in sys.modules]
    if len(loaded) > 1:
        raise BindingError("PyQt6 and PySide6 are both loaded; use only one per process.")
    forced = os.environ.get("FLUENT_BLUE_QT_BINDING")
    if forced and forced not in SUPPORTED_BINDINGS:
        raise BindingError(f"FLUENT_BLUE_QT_BINDING must be one of {SUPPORTED_BINDINGS}, got {forced!r}.")
    if loaded:
        if forced and forced != loaded[0]:
            raise BindingError(f"FLUENT_BLUE_QT_BINDING={forced} but {loaded[0]} is already loaded.")
        return loaded[0]
    if forced:
        return forced
    for name in SUPPORTED_BINDINGS:
        try:
            importlib.import_module(f"{name}.QtCore")
        except ImportError:
            continue
        return name
    raise BindingError("Fluent Blue needs a Qt binding: pip install 'fluent-blue[pyqt6]' or 'fluent-blue[pyside6]'.")


BINDING = _select_binding()

# The Linux wheels of PySide6 6.9 to 6.12 corrupt the reference count of True/False whenever
# a Python-declared Signal is emitted (the macOS wheels do not). Python 3.12 makes those
# objects immortal, so the fault is harmless there; on 3.11 the interpreter aborts after a
# few hundred emits.
PYSIDE_MIN_PYTHON_ON_LINUX = (3, 12)
if BINDING == "PySide6" and sys.platform.startswith("linux") and sys.version_info < PYSIDE_MIN_PYTHON_ON_LINUX:
    import warnings

    warnings.warn(
        "On Linux, Fluent Blue supports PySide6 on Python 3.12 or newer: the Linux wheels of PySide6 6.9 to 6.12 "
        "corrupt reference counts when custom signals are emitted on Python 3.11, and the process can abort. "
        "Use Python 3.12+ or PyQt6.",
        RuntimeWarning, stacklevel=2,
    )

QtCore = importlib.import_module(f"{BINDING}.QtCore")
QtGui = importlib.import_module(f"{BINDING}.QtGui")
QtWidgets = importlib.import_module(f"{BINDING}.QtWidgets")
QtSvg = importlib.import_module(f"{BINDING}.QtSvg")

if BINDING == "PyQt6":
    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    Property = QtCore.pyqtProperty
    BINDING_VERSION = QtCore.PYQT_VERSION_STR
else:
    Signal = QtCore.Signal
    Slot = QtCore.Slot
    Property = QtCore.Property
    BINDING_VERSION = importlib.import_module(BINDING).__version__

QT_VERSION = QtCore.qVersion()


def delete_now(obj) -> None:
    """Destroy a QObject immediately, so app-wide restyling no longer has to visit it.

    Deletion goes through Qt's deferred delete, which works identically on both bindings. Do
    not disconnect Python slots first: ``disconnect`` of a bound method on PySide6 6.12 with
    Python 3.11 corrupts the reference count of ``True``/``False`` and aborts the process
    later, whereas destroying a connected receiver is clean.
    """
    if isinstance(obj, QtWidgets.QWidget):
        obj.hide()
        obj.setParent(None)
    obj.deleteLater()
    QtCore.QCoreApplication.sendPostedEvents(obj, QtCore.QEvent.Type.DeferredDelete.value)


SignalInstanceTypes = (QtCore.pyqtBoundSignal,) if BINDING == "PyQt6" else (QtCore.SignalInstance,)
SignalTypes = (QtCore.pyqtSignal,) if BINDING == "PyQt6" else (QtCore.Signal,)

# Re-export every Qt class so components can write
# ``from fluent_blue.compatibility.qt import QFrame, Qt, Signal``.
for _module in (QtCore, QtGui, QtWidgets, QtSvg):
    for _name in dir(_module):
        if _name.startswith("Q") and _name != "QT_VERSION":
            globals()[_name] = getattr(_module, _name)
del _module, _name
