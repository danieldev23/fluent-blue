"""Theme switching must survive deleted widgets, and refresh hidden ones when they next appear."""
import pytest

from fluent_blue import IconButton, ThemeManager
from fluent_blue.compatibility.qt import QApplication, QImage, QWidget, delete_now
from fluent_blue.studio import catalog

ENTRIES = catalog.entries()


@pytest.fixture(autouse=True)
def light_theme(qapp):
    ThemeManager.set_theme("light")
    yield
    ThemeManager.set_theme("light")


@pytest.mark.parametrize("entry", ENTRIES, ids=lambda e: e.name)
def test_switch_after_component_is_deleted(entry, qapp):
    """A signal connected to a deleted widget raises, which PyQt turns into an abort."""
    errors = []
    import sys

    previous, sys.excepthook = sys.excepthook, lambda *info: errors.append(info)
    try:
        demo = entry.run()
        demo.show()
        qapp.processEvents()
        delete_now(demo)
        ThemeManager.set_theme("dark")
        qapp.processEvents()
    finally:
        sys.excepthook = previous
    assert errors == []


def test_hidden_widget_refreshes_when_shown(qtbot):
    host = QWidget()
    qtbot.addWidget(host)
    button = IconButton("bell", host, tooltip="Bell")
    host.hide()
    before = button.icon().pixmap(16, 16).toImage().convertToFormat(QImage.Format.Format_ARGB32).copy()
    ThemeManager.set_theme("dark")
    host.show()
    qtbot.waitExposed(host)
    assert button.icon().pixmap(16, 16).toImage().convertToFormat(QImage.Format.Format_ARGB32) != before


def test_switching_does_not_reapply_the_qt_style(qapp, monkeypatch):
    ThemeManager.set_theme("dark")
    calls = []
    monkeypatch.setattr(QApplication, "setStyle", lambda *a: calls.append(a))
    ThemeManager.set_theme("light")
    assert calls == []
