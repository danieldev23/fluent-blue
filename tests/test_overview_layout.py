"""The Overview board keeps the designed three-band layout on a 1536 px window, and never scrolls sideways."""
import pytest

from fluent_blue import ThemeManager
from fluent_blue.studio.app import StudioWindow


def _open(qtbot, width, height):
    ThemeManager.set_theme("light")
    window = StudioWindow()
    qtbot.addWidget(window)
    window.resize(width, height)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(30)
    return window, window.pages["Overview"]


def test_designed_layout_at_1536(qtbot):
    _, page = _open(qtbot, 1536, 1024)
    assert [len(row) for row in page._current_rows] == [3, 5, 4]


@pytest.mark.parametrize(("width", "height"), [(1536, 1024), (1366, 768), (1280, 720), (1024, 680)])
def test_no_horizontal_scrolling(qtbot, width, height):
    _, page = _open(qtbot, width, height)
    assert page.scroll_area.horizontalScrollBar().maximum() == 0
