"""Headless Qt for all tests. Select the binding with FLUENT_BLUE_QT_BINDING."""
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from fluent_blue.compatibility.qt import BINDING  # noqa: E402

os.environ.setdefault("PYTEST_QT_API", BINDING.lower())
