"""The Overview board wraps its tiles to the available width and never scrolls sideways.

The reflow is tested through ``_reflow(width)`` rather than by resizing the window: headless
platforms clamp top-level windows to a small virtual screen, which would test the clamp, not
the layout. Tile widths depend on the platform's fonts, so the exact three-row design is
asserted only where it was verified; elsewhere each band may wrap once.
"""
import sys

import pytest

from fluent_blue import ThemeManager
from fluent_blue.studio.app import StudioWindow

DESIGNED_PAGE_WIDTH = 1340  # A 1536 px window minus the sidebar.


def _open(qtbot, width=1536, height=1024):
    ThemeManager.set_theme("light")
    window = StudioWindow()
    qtbot.addWidget(window)
    window.resize(width, height)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(30)
    return window, window.pages["Overview"]


def _widths(page):
    return [[max(tile.minimumSizeHint().width(), tile.minimumWidth()) for tile, _ in page._bands]]


def test_designed_width_keeps_every_band_compact(qtbot):
    _, page = _open(qtbot)
    page._reflow(DESIGNED_PAGE_WIDTH)
    rows = [len(row) for row in page._current_rows]
    assert rows[0] == 3, f"hero band wrapped: {rows}, widths {_widths(page)}"
    assert len(rows) <= 5, f"a band wrapped more than once: {rows}, widths {_widths(page)}"
    assert sum(rows) == sum(len(band) for band in page._bands)


@pytest.mark.skipif(sys.platform != "darwin", reason="The exact three-row design is verified with the macOS system font.")
def test_designed_three_row_layout(qtbot):
    _, page = _open(qtbot)
    page._reflow(DESIGNED_PAGE_WIDTH)
    assert [len(row) for row in page._current_rows] == [3, 5, 4], _widths(page)


def test_narrow_widths_wrap_instead_of_overflowing(qtbot):
    _, page = _open(qtbot)
    for width in (1180, 1000, 820):
        page._reflow(width)
        assert all(len(row) >= 1 for row in page._current_rows)
        assert sum(len(row) for row in page._current_rows) == sum(len(band) for band in page._bands)


@pytest.mark.parametrize(("width", "height"), [(1536, 1024), (1366, 768), (1280, 720), (1024, 680)])
def test_no_horizontal_scrolling(qtbot, width, height):
    _, page = _open(qtbot, width, height)
    assert page.scroll_area.horizontalScrollBar().maximum() == 0
